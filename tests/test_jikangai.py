import unittest
from datetime import datetime, timedelta
from jikangai import BreakTime, LegalHoliday


class TestLegalHoliday(unittest.TestCase):

    def test_initialization(self):
        holiday = LegalHoliday(2, 3)
        self.assertEqual(holiday.week_number_of_4weeks, 2)
        self.assertEqual(holiday.weekday, 3)

    def test_of_every_sunday(self):
        holidays = LegalHoliday.of_every_sunday()
        self.assertEqual(len(holidays), 4)
        for i, holiday in enumerate(holidays, start=1):
            self.assertEqual(holiday.week_number_of_4weeks, i)
            self.assertEqual(holiday.weekday, 7)


class TestBreakTime(unittest.TestCase):

    def test_initialization(self):
        start = datetime(2024, 3, 17, 9, 0)
        end = datetime(2024, 3, 17, 9, 30)
        break_time = BreakTime(start, end)
        self.assertEqual(break_time.start, start)
        self.assertEqual(break_time.end, end)

    def test_value_method(self):
        start = datetime(2024, 3, 17, 9, 0)
        end = datetime(2024, 3, 17, 9, 30)
        break_time = BreakTime(start, end)
        expected_value = timedelta(minutes=30)
        self.assertEqual(break_time.value(), expected_value)

    def test_invalid_initialization(self):
        start = datetime(2024, 3, 17, 9, 30)
        end = datetime(2024, 3, 17, 9, 0)
        with self.assertRaises(ValueError):
            BreakTime(start, end)

if __name__ == '__main__':
    unittest.main()
