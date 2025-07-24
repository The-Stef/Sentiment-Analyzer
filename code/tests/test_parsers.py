from sentinalysis.parsers import get_txt, get_csv, get_json
import unittest
import datetime
import ijson, json

class TestParsers(unittest.TestCase):
    """
    Checks that the get_txt() function behaves as expected by providing some typical input.
    """
    def test_provide_basic_line_txt(self):
        typical_line = """7/23/25, 16:45 - TestPerson: This is a test."""
        result_tuple = get_txt(typical_line)

        self.assertIsInstance(result_tuple, tuple, "Result is not a tuple.")

        self.assertEqual(result_tuple[0], datetime.date(2025, 7, 23))
        self.assertEqual(result_tuple[1], "TestPerson", "Actual username different than expected.")
        self.assertEqual(result_tuple[2], "This is a test.", "Actual message different than expected.")

    """
    The get_txt() should work with both single and double digits for days and months. 
    This test checks that.
    """
    def test_check_if_date_works_with_single_digits_as_well_txt(self):
        single_digit_month = """11/3/25, 16:00 - TestPerson: This is a test."""
        single_digit_day = """1/12/25, 17:30 - TestPerson: This is a test."""
        single_digit_month_day = """7/3/25, 21:26 - TestPerson: This is a test."""

        result_tuple = get_txt(single_digit_month)
        self.assertEqual(result_tuple[0], datetime.date(2025, 11, 3), "The single digit month was improperly handled.")
        
        result_tuple = get_txt(single_digit_day)
        self.assertEqual(result_tuple[0], datetime.date(2025, 1, 12), "The single digit day was improperly handled.")

        result_tuple = get_txt(single_digit_month_day)
        self.assertEqual(result_tuple[0], datetime.date(2025, 7, 3), "The single digit month and day were improperly handled.")

    """
    There is a possibility of a message including extra colons, this test checks how that event is handled.
    """
    def test_check_how_extra_colons_in_message_are_handled_txt(self):
        typical_line = """7/23/25, 16:45 - TestPerson: Here is the test: Check how the extra colon is handled."""
        result_tuple = get_txt(typical_line)

        self.assertEqual(result_tuple[2], "Here is the test: Check how the extra colon is handled.", "An extra colon in the message was not handled by the get_txt() function.")

    """
    Checks that the get_csv() function behaves as expected by providing some typical input.
    """
    def test_provide_basic_line_csv(self):

        typical_line = """7/23/25,16:45,TestPerson,This is a test."""
        result_tuple = get_csv(typical_line)

        self.assertIsInstance(result_tuple, tuple, "Result is not a tuple.")

        self.assertEqual(result_tuple[0], datetime.date(2025, 7, 23))
        self.assertEqual(result_tuple[1], "TestPerson", "Actual username different than expected.")
        self.assertEqual(result_tuple[2], "This is a test.", "Actual message different than expected.")

    """
    The get_csv() should work with both single and double digits for days and months. 
    This test checks that.
    """
    def test_check_if_date_works_with_single_digits_as_well_csv(self):
        single_digit_month = """11/3/25,16:00,TestPerson,This is a test."""
        single_digit_day = """1/12/25,17:30,TestPerson,This is a test."""
        single_digit_month_day = """7/3/25,21:26,TestPerson,This is a test."""

        result_tuple = get_csv(single_digit_month)
        self.assertEqual(result_tuple[0], datetime.date(2025, 11, 3), "The single digit month was improperly handled.")
        
        result_tuple = get_csv(single_digit_day)
        self.assertEqual(result_tuple[0], datetime.date(2025, 1, 12), "The single digit day was improperly handled.")

        result_tuple = get_csv(single_digit_month_day)
        self.assertEqual(result_tuple[0], datetime.date(2025, 7, 3), "The single digit month and day were improperly handled.")

    """
    There is a possibility of a message including extra colons, this test checks how that event is handled.
    """
    def test_check_how_extra_colons_in_message_are_handled_csv(self):
        typical_line = """7/23/25,16:45,TestPerson,Here is the test: Check how the extra colon is handled."""
        result_tuple = get_csv(typical_line)

        self.assertEqual(result_tuple[2], "Here is the test: Check how the extra colon is handled.", "An extra colon in the message was not handled by the get_csv() function.")


    # ------------ jsn ------------

    """
    Checks that the get_json() function behaves as expected by providing some typical input.
    """
    def test_provide_basic_line_json(self):
        typical_obj = json.loads('{"date":"7/23/25","time":"16:45","username":"TestPerson","message":"This is a test."}')
        result_tuple = get_json(typical_obj)

        self.assertIsInstance(result_tuple, tuple, "Result is not a tuple.")

        self.assertEqual(result_tuple[0], datetime.date(2025, 7, 23))
        self.assertEqual(result_tuple[1], "TestPerson", "Actual username different than expected.")
        self.assertEqual(result_tuple[2], "This is a test.", "Actual message different than expected.")

    """
    The get_json() should work with both single and double digits for days and months. 
    This test checks that.
    """
    def test_check_if_date_works_with_single_digits_as_well_json(self):
        single_digit_month = json.loads('{"date":"11/3/25","time":"16:00","username":"TestPerson","message":"This is a test."}')
        single_digit_day = json.loads('{"date":"1/12/25","time":"17:30","username":"TestPerson","message":"This is a test."}')
        single_digit_month_day = json.loads('{"date":"7/3/25","time":"21:26","username":"TestPerson","message":"This is a test."}')

        result_tuple = get_json(single_digit_month)
        self.assertEqual(result_tuple[0], datetime.date(2025, 11, 3), "The single digit month was improperly handled.")
        
        result_tuple = get_json(single_digit_day)
        self.assertEqual(result_tuple[0], datetime.date(2025, 1, 12), "The single digit day was improperly handled.")

        result_tuple = get_json(single_digit_month_day)
        self.assertEqual(result_tuple[0], datetime.date(2025, 7, 3), "The single digit month and day were improperly handled.")

    """
    There is a possibility of a message including extra colons, this test checks how that event is handled.
    """
    def test_check_how_extra_colons_in_message_are_handled_json(self):
        typical_obj = json.loads('{"date":"7/23/25","time":"16:45","username":"TestPerson","message":"Here is the test: Check how the extra colon is handled."}')
        result_tuple = get_json(typical_obj)

        self.assertEqual(result_tuple[2], "Here is the test: Check how the extra colon is handled.", "An extra colon in the message was not handled by the get_json() function.")
