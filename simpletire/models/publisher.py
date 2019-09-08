import pdb

class Publisher:

    TIRE_FILE_TEMP_LOCAL = '/tmp/tires.csv'
    READINGS_FILE_TEMP_LOCAL = '/tmp/readings.csv'
    BUCKET_NAME_TIRES = 'bip-price-monitor-tires'
    BUCKET_NAME_READINGS = 'bip-price-monitor-readings'
    TIRE_FILE_REMOTE = 'tires.csv'
    DELIMITER = '|'

    @classmethod
    def publish(cls):
        cls.write_tires_to_csv()
        cls.write_todays_readings_to_csv()

        # Importing late so that importing this module does not actually load boto3
        # Therefore saving memory
        import boto3
        s3 = boto3.client('s3')

        s3.upload_file(cls.TIRE_FILE_TEMP_LOCAL,
                       cls.BUCKET_NAME_TIRES,
                       cls.TIRE_FILE_REMOTE)

        s3.upload_file(cls.READINGS_FILE_TEMP_LOCAL,
                       cls.BUCKET_NAME_READINGS,
                       cls._readings_file_remote())

    @classmethod
    def write_tires_to_csv(cls):
        with open(cls.TIRE_FILE_TEMP_LOCAL, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=cls.DELIMITER)
            for tire in Tire.objects.all():
                row = [tire.id, tire.name, tire.path]
                writer.writerow(row)

    @classmethod
    def write_todays_readings_to_csv(cls):
        with open(cls.READINGS_FILE_TEMP_LOCAL, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=cls.DELIMITER)
            for reading in Reading.objects.filter(date=Util.today_string()):
                row = [reading.id, reading.tire_id, reading.date, reading.price_pennies, reading.in_stock]
                writer.writerow(row)

    @classmethod
    def _readings_file_remote(cls):
        today_string = Util.today_string()
        return f'readings-{today_string}'

    # Column names are only here for pasting into Amazon Athena
    # during table definition
    #
    @classmethod
    def _tire_column_names(cls):
        '''
        id int,
        name string,
        path string
        '''

    @classmethod
    def _reading_column_names(cls):
        '''
        id int,
        tire_id int,
        date string,
        price_pennies int,
        in_stock boolean
        '''
