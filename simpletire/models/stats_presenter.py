import io
import ipdb
import math
import pandas

class StatsPresenter:
    class Meta:
        app_label = 'simpletire'

    PENNIES_PER_DOLLAR = 100
    DEFAULT_SORT_KEY = 'mean'
    STATUS_SUCCEEDED = 'SUCCEEDED'
    POLL_PERIOD_SECONDS = 0.5


    @classmethod
    def tire_stats(cls):
        #tires = cls._tires_from_postgres()
        tires = cls._tires_from_aws_athena()
        output = []
        for tire in tires:
            tire_dict = dict(id=tire.id,
                             name=tire.name,
                             path=tire.path,
                             num_readings=tire.num_readings,
                             min=tire.min_pennies / cls.PENNIES_PER_DOLLAR,
                             max=tire.max_pennies / cls.PENNIES_PER_DOLLAR,
                             mean=tire.mean_pennies / cls.PENNIES_PER_DOLLAR,
                             std=(tire.std_pennies or 0) / cls.PENNIES_PER_DOLLAR,
                             current=tire.current_pennies / cls.PENNIES_PER_DOLLAR)

            if math.isnan(tire_dict['std']):
                del tire_dict['std']

            output.append(tire_dict)
        return output

    @classmethod
    def tire_stats_sorted(cls, sort_key, reverse):
        stats = cls.tire_stats()

        if sort_key not in stats[0].keys():
            sort_key = cls.DEFAULT_SORT_KEY

        key = lambda x: x[sort_key]
        stats.sort(key=key, reverse=reverse)
        return stats

    @classmethod
    def _tires_from_postgres(cls):
        tires = Tire.objects.raw(cls._query_postgres())
        return tires

    @classmethod
    def _tires_from_aws_athena(cls):
        # see http://www.ilkkapeltola.fi/2018/04/simple-way-to-query-amazon-athena-in.html
        client = boto3.client('athena',
                              region_name='us-west-2')


        response = client.start_query_execution(
                    QueryString=cls._query_prestodb(),
                    QueryExecutionContext={ 'Database': 'price_monitor' },
                    ResultConfiguration={
                        'OutputLocation': 's3://bip-price-monitor-athena-result-sets/'
                      }
                    )


        execution_id = response['QueryExecutionId']
        status = None
        while status != cls.STATUS_SUCCEEDED:
            time.sleep(cls.POLL_PERIOD_SECONDS)
            result = client.get_query_execution(QueryExecutionId = execution_id)
            status = result['QueryExecution']['Status']['State']
            print('waiting for query to complete')


        s3client = boto3.client('s3')

        obj = s3client.get_object(Bucket='bip-price-monitor-athena-result-sets',
                                  Key= f'{execution_id}.csv')

        df = pandas.read_csv(io.BytesIO(obj['Body'].read()))

        return df.itertuples()




    @classmethod
    def _query_postgres(cls):
        # Uses postgres-specific "DISTINCT ON"
        return '''
        SELECT t.id, name, path, num_readings, min_pennies, max_pennies, mean_pennies, std_pennies, current_pennies FROM simpletire_tire t
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
             ON stats.tire_id = currents.tire_id;'''

    @classmethod
    def _query_generic(cls):
        # Uses windowing instead of postgres-specific "DISTINCT ON"
        return '''
        SELECT t.id, name, path, num_readings, min_pennies, max_pennies, mean_pennies, std_pennies, current_pennies FROM simpletire_tire t
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
           ON stats.tire_id = currents.tire_id;'''

    @classmethod
    def _query_prestodb(cls):
        # PrestoDB uses true and false as booleans instead of 't' and 'f'
        return cls._query_generic().replace("= 't'", "= true")
