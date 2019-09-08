import boto3
import io
import pdb
import math
import pandas
from .tire import Tire
from django.db import connection

class StatsPresenter:

    PENNIES_PER_DOLLAR = 100
    STATUS_SUCCEEDED = 'SUCCEEDED'
    POLL_PERIOD_SECONDS = 0.5


    def __init__(self, sql_filter='', limit=0):
        self.sql_filter = sql_filter
        self.sql_limit = ''
        if limit:
            self.sql_limit = f'LIMIT {limit}'

    def tire_stats(self):
        # This "can" push data to aws athena and pull from it,
        # but the response time is 2-3 seconds for only a couple
        # thousand readings. Going back to postgres-only
        #tires = self._tires_from_aws_athena()

        tires = self._tires_from_postgres()
        output = []
        for tire in tires:

            tire_dict = dict(id=tire.id,
                             name=tire.name,
                             path=tire.path,
                             size=tire.size,
                             num_readings=tire.num_readings,
                             min=tire.min_pennies / self.PENNIES_PER_DOLLAR,
                             max=tire.max_pennies / self.PENNIES_PER_DOLLAR,
                             mean=tire.mean_pennies / self.PENNIES_PER_DOLLAR,
                             std=(tire.std_pennies or 0) / self.PENNIES_PER_DOLLAR,
                             current=tire.current_pennies / self.PENNIES_PER_DOLLAR,
                             utqg=tire.utqg,
                             diameter=tire.diameter)

            if math.isnan(tire_dict['std']):
                del tire_dict['std']

            output.append(tire_dict)
        return output

    def matching_records_count(self):
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT count(*) FROM simpletire_tire {self.sql_filter}')
            return cursor.fetchone()[0]

    def _tires_from_postgres(self):
        tires = Tire.objects.raw(self._query_postgres())
        return tires

    def _tires_from_aws_athena(self):
        # see http://www.ilkkapeltola.fi/2018/04/simple-way-to-query-amazon-athena-in.html
        client = boto3.client('athena',
                              region_name='us-west-2')


        response = client.start_query_execution(
                    QueryString=self._query_prestodb(),
                    QueryExecutionContext={ 'Database': 'price_monitor' },
                    ResultConfiguration={
                        'OutputLocation': 's3://bip-price-monitor-athena-result-sets/'
                      }
                    )


        execution_id = response['QueryExecutionId']
        status = None
        while status != self.STATUS_SUCCEEDED:
            time.sleep(self.POLL_PERIOD_SECONDS)
            result = client.get_query_execution(QueryExecutionId = execution_id)
            status = result['QueryExecution']['Status']['State']
            print('waiting for query to complete')


        s3client = boto3.client('s3')

        obj = s3client.get_object(Bucket='bip-price-monitor-athena-result-sets',
                                  Key= f'{execution_id}.csv')

        df = pandas.read_csv(io.BytesIO(obj['Body'].read()))

        return df.itertuples()




    def _query_postgres(self):
        # Uses postgres-specific "DISTINCT ON"
        return f'''
        SELECT t.id, section_width, aspect_ratio, wheel_diameter, name, path, num_readings, min_pennies, max_pennies, mean_pennies, std_pennies, current_pennies FROM simpletire_tire t
          JOIN
            (
             SELECT
                tire_id,
                count(*) as num_readings,
                avg(price_pennies)  AS mean_pennies,
                min(price_pennies)  AS min_pennies,
                max(price_pennies)  AS max_pennies,
                stddev_samp(price_pennies) AS std_pennies
              FROM simpletire_reading
              WHERE in_stock = 't'
              GROUP BY tire_id
            ) AS stats
            ON t.id = stats.tire_id

          JOIN
            (
              SELECT DISTINCT ON (tire_id) tire_id, date, price_pennies as current_pennies
              FROM simpletire_reading
              ORDER BY tire_id, date DESC
             ) AS currents
             ON stats.tire_id = currents.tire_id
        {self.sql_filter}
        ORDER BY mean_pennies, t.id
        {self.sql_limit};'''

    def _query_generic(self):
        # Uses windowing instead of postgres-specific "DISTINCT ON"
        return f'''
        SELECT t.id, section_width, aspect_ratio, wheel_diameter, name, path, num_readings, min_pennies, max_pennies, mean_pennies, std_pennies, current_pennies FROM simpletire_tire t
          JOIN
            (
             SELECT
                tire_id,
                count(*) as num_readings,
                avg(price_pennies)  AS mean_pennies,
                min(price_pennies)  AS min_pennies,
                max(price_pennies)  AS max_pennies,
                stddev_samp(price_pennies) AS std_pennies
              FROM simpletire_reading
              WHERE in_stock = 't'
              GROUP BY tire_id
            ) AS stats
            ON t.id = stats.tire_id

          JOIN
            (
            SELECT tire_id, price_pennies as current_pennies, date
            FROM
              (
                SELECT tire_id,
                       price_pennies,
                       date,
                       max(date) OVER (PARTITION BY tire_id) as max_date
                FROM simpletire_reading
                ORDER BY tire_id, date DESC
               ) AS currents_temp WHERE date = max_date
            ) AS currents
           ON stats.tire_id = currents.tire_id
        {self.sql_filter}
        ORDER BY mean_pennies, t.id
        {self.sql_limit};'''

    def _query_prestodb(self):
        # PrestoDB uses true and false as booleans instead of 't' and 'f'
        return self._query_generic().replace("= 't'", "= true")
