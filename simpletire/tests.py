from django.test import TestCase
from simpletire.models import Tire

# Create your tests here.

class TireTestCase(TestCase):

    def create_four_tires(self):
        tire_1 = Tire(path='blahblah-225-50zr17blah')
        tire_2 = Tire(path='blahblah-245-45zr18blah')
        tire_3 = Tire(path='blahblah-205-50zr17blah')
        tire_4 = Tire(path='blahblah-245-50zr18blah')

        tire_1.save()
        tire_2.save()
        tire_3.save()
        tire_4.save()

    # Yes, we are testing private methods

    def test_filter_by_size_regex_1(self):
        expected = '(\\d{3})-(\\d{2})z?r(\\d{2})'
        self.assertEqual(expected , Tire.filter_by_size_regex())

    def test_filter_by_size_regex_2(self):
        expected = '(225)-(\\d{2})z?r(\\d{2})'
        self.assertEqual(expected , Tire.filter_by_size_regex(section_width=225))

    def test_filter_by_size_regex_3(self):
        expected = '(\\d{3})-(45)z?r(\\d{2})'
        self.assertEqual(expected , Tire.filter_by_size_regex(profile=45))

    def test_filter_by_size_regex_4(self):
        expected = '(\\d{3})-(\\d{2})z?r(18)'
        self.assertEqual(expected , Tire.filter_by_size_regex(wheel_diameter=18))


    def test_filter_by_size_1(self):
        self.create_four_tires()
        tires = Tire.filter_by_size()
        self.assertEqual(len(tires), 4)

    def test_filter_by_size_2(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(section_width=225)
        self.assertEqual(len(tires), 1)

    def test_filter_by_size_2(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(section_width=195)
        self.assertEqual(len(tires), 0)

    def test_filter_by_size_2(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(section_width=245)
        self.assertEqual(len(tires), 2)


    def test_filter_by_size_3(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(profile=60)
        self.assertEqual(len(tires), 0)

    def test_filter_by_size_3(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(profile=45)
        self.assertEqual(len(tires), 1)

    def test_filter_by_size_4(self):
        self.create_four_tires()
        tires = Tire.filter_by_size(profile=50)
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

