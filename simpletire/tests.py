from django.test import TestCase
from simpletire.models import Tire
import pdb

# Create your tests here.

class TireTestCase(TestCase):

    def create_four_tires(self):
        tire_1 = Tire(path='blahblah-225-50zr17blah-tires')
        tire_2 = Tire(path='blahblah-245-45zr18blah-tires')
        tire_3 = Tire(path='blahblah-205-50zr17blah-tires')
        tire_4 = Tire(path='blahblah-245-50zr18blah-tires')

        tire_1.set_dimensions()
        tire_2.set_dimensions()
        tire_3.set_dimensions()
        tire_4.set_dimensions()

        tire_1.save()
        tire_2.save()
        tire_3.save()
        tire_4.save()


    def test_filter_by_size_1(self):
        self.create_four_tires()
        tires = Tire.filter_by_size()
        self.assertEqual(len(tires), 4)

    def test_filter_by_size_2(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(section_width=225)
        self.assertEqual(len(tires), 3)

    def test_filter_by_size_2(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(section_width=195)
        self.assertEqual(len(tires), 4)

    def test_filter_by_size_2(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(section_width=255)
        self.assertEqual(len(tires), 0)

    def test_filter_by_size_3(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(aspect_ratio=60)
        self.assertEqual(len(tires), 0)

    def test_filter_by_size_3(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(aspect_ratio=45)
        self.assertEqual(len(tires), 4)

    def test_filter_by_size_4(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(aspect_ratio=55)
        self.assertEqual(len(tires), 3)

    def test_filter_by_size_5(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(wheel_diameter=30)
        self.assertEqual(len(tires), 0)

    def test_filter_by_size_5(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(wheel_diameter=17)
        self.assertEqual(len(tires), 2)

    def test_filter_by_size_5(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(wheel_diameter=18)
        self.assertEqual(len(tires), 2)


    def test_size(self):
        tire = Tire(section_width=225, aspect_ratio=50, wheel_diameter=17)
        self.assertEqual(tire.size, '225/50r17')

    def test_set_dimensions(self):
        tire = Tire(path='blahblah-235-40r18blah-tires')
        tire.set_dimensions()
        self.assertEqual(235, tire.section_width)
        self.assertEqual(40,  tire.aspect_ratio)
        self.assertEqual(18,  tire.wheel_diameter)

    def test_sql_filter_1(self):
        sql = Tire.sql_filter(aspect_ratio=30)
        self.assertEqual('WHERE aspect_ratio IN (30, 35, 25)', sql)

    def test_sql_filter_1(self):
        sql = Tire.sql_filter(section_width=225)
        self.assertEqual('WHERE section_width >= 225', sql)

    def test_sql_filter_1(self):
        sql = Tire.sql_filter(wheel_diameter=16)
        self.assertEqual('WHERE wheel_diameter = 16', sql)

    def test_diameter(self):
        # Ten-inch section width
        tire = Tire(path='blahblah-254-40r17blah-tires')
        tire.set_dimensions()
        self.assertEqual(25, tire.diameter)

