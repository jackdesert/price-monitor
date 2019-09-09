import math
import pdb

from django.db import connection
from simpletire.models.tire import Tire

class StatsPresenter:

    TABLE_NAME = 'simpletire_aggregate'
    PENNIES_PER_DOLLAR = 100

    def __init__(self, sql_filter='', limit=0):
        self.sql_filter = sql_filter
        self.sql_limit = ''
        if limit:
            self.sql_limit = f'LIMIT {limit}'

    def tire_stats(self):
        tires = self._tires()
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
            cursor.execute(f'SELECT count(*) FROM {self.TABLE_NAME} {self.sql_filter}')
            return cursor.fetchone()[0]

    def _tires(self):
        tires = Tire.objects.raw(self._tires_query())
        return tires


    def _tires_query(self):
        return f'''SELECT *
                   FROM {self.TABLE_NAME}
                   {self.sql_filter}
                   {self.sql_limit}'''


    @classmethod
    def load(cls):
        print(f'*** LOADING AGGREGATES ***')
        with connection.cursor() as cursor:
            query = cls._recreate_table_and_load_aggregates_query()
            cursor.execute(query)

    @classmethod
    def _recreate_table_and_load_aggregates_query(cls):
        return f''' BEGIN;
                    DROP TABLE IF EXISTS {cls.TABLE_NAME};
                    CREATE TABLE {cls.TABLE_NAME} AS {cls._aggregate_query()};
                    COMMIT;
                    ANALYZE {cls.TABLE_NAME}'''


    @classmethod
    def _aggregate_query(cls):
        # Uses postgres-specific "DISTINCT ON"
        return '''
        SELECT t.id, section_width, aspect_ratio, wheel_diameter, utqg, name, path, num_readings, min_pennies, max_pennies, mean_pennies, std_pennies, current_pennies FROM simpletire_tire t
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
        ORDER BY mean_pennies, t.id'''



