from sentinalysis.converters import convert_txt_to_json, convert_txt_to_csv
import pandas as pd
import unittest
import json
import os
import re

class TestConverters(unittest.TestCase):
    """
    Checks if the convert_txt_to_json function returns expected output.
    Converts validated .txt input to .json, and checks whether the JSON object components contain the proper information.
    """
    def test_correct_conversion_to_json_file(self):
        file_name = "test-sentinalysis-json-conversion.txt"
        file_name_json = "test-sentinalysis-json-conversion.json"

        with open(file_name, "w") as f1:
            f1.write("""7/23/25, 16:45 - TestPerson: This is a test.""")
        converted_json = convert_txt_to_json(file_name)
        os.remove(file_name)

        with open(converted_json, "r") as f2:
            data = json.load(f2)
        os.remove(file_name_json)

        self.assertEqual(data[0]["date"], "7/23/25", "The actual date differs from the expected date.")
        self.assertEqual(data[0]["message"], "This is a test.", "The actual message differs from the expected message.")
        self.assertEqual(data[0]["time"], "16:45", "The actual time differs from the expected time.")
        self.assertEqual(data[0]["username"], "TestPerson", "The actual username differs from the expected username.")

    """
    Checks to see if convert_txt_to_json messes the JSON formatting by adding extra commas in the file.
    Takes multi-line validated input, checks if first / last character is a comma. 
    The number of remaining inter-object commas must be the number of objects - 1.
    """
    def test_ensure_proper_formatting_of_json_result_with_no_extra_commas(self):
        file_name = "test-sentinalysis-json-conversion.txt"
        file_name_json = "test-sentinalysis-json-conversion.json"

        with open(file_name, "w") as f1:
            f1.write("""7/23/25, 16:45 - TestPerson1: This is another test.\n8/23/25, 12:36 - TestPerson2: This test contains multiple messages, actually.""")
        converted_json = convert_txt_to_json(file_name)
        os.remove(file_name)

        with open(converted_json, "r") as f2:
            data = f2.read()
        os.remove(file_name_json)

        obj_count = len(json.loads(data))

        self.assertFalse(data.startswith(','), "JSON object array contains a leading comma.")
        self.assertFalse(data.endswith(','), "JSON object array contains a trailing comma.")

        object_pattern = r"\{[^{}]*\}"
        inter_object_commas = re.sub(object_pattern, '', data)

        self.assertEqual(inter_object_commas.count(','), obj_count - 1, "Actual number of inter-object commas different than expected.")

    """
    Checks whether the returned path is absolute and has the .json file suffix.
    """
    def test_check_path_returned_by_json_conversion_function(self):
        file_name = "test-sentinalysis-json-abspath-check.txt"
        with open(file_name, "w") as f:
            f.write("""7/14/22, 21:09 - TestPerson: This is a test.""")
        result_path = convert_txt_to_json(file_name)
        os.remove(file_name)

        self.assertTrue(os.path.isabs(result_path), "Returned path is not absolute.")
        self.assertTrue(result_path.endswith(".json"), f"Returned path does not contain the '.json' extension at the end: {result_path}")
        os.remove(result_path)

    """
    Checks if the json conversion function throws an error when provided with an incorrect path.
    Only Windows paths are tested at the moment.
    """
    def test_provide_non_existent_path_to_json_conversion_function(self):
        file_name1= "test-sentinalysis-non-existent-file.txt"
        with self.assertRaises(FileNotFoundError):
            convert_txt_to_json(file_name1)
        
        file_name2 = "C:\\Users\\username\\AppData\\Roaming\\nltk_data\\sentiment\\vader_lexicon.txt"
        with self.assertRaises(FileNotFoundError):
            convert_txt_to_json(file_name2)

    """
    Checks whether or not the header of the .csv file is the expected one.
    """
    def test_check_csv_converter_header(self):
        file_name = "test-sentinalysis-csv-conversion.txt"
        file_name_csv = "test-sentinalysis-csv-conversion.csv"

        with open(file_name, "w") as f1:
            f1.write("""7/23/25, 16:45 - TestPerson: This is a test.""")
        converted_csv = convert_txt_to_csv(file_name)
        os.remove(file_name)

        with open(converted_csv, "r") as f2:
            data = f2.read()
        os.remove(file_name_csv)

        first_row = data.partition("\n")
        self.assertEqual(first_row[0], 'Date,Time,Username,Message', f"The .csv file header is different than what it should be: {first_row[0]}")

    """
    Checks if the convert_txt_to_json function returns expected output.
    """
    def test_check_correct_conversion_to_csv_file(self):
        file_name = "test-sentinalysis-csv-commas.txt"
        file_name_csv = "test-sentinalysis-csv-commas.csv"

        with open(file_name, "w") as f1:
            f1.write("""4/16/21, 14:10 - TestPerson: This is a csv test.""")
        convert_txt_to_csv(file_name)
        os.remove(file_name)

        data = pd.read_csv(file_name_csv)
        os.remove(file_name_csv)

        self.assertEqual(data.at[0, "Date"], "4/16/21", "Date in the csv file is different than expected.")
        self.assertEqual(data.at[0, "Time"], "14:10", "Time in the csv file is different than expected.")
        self.assertEqual(data.at[0, "Username"], "TestPerson", "Username in the csv file is different than expected.")
        self.assertEqual(data.at[0, "Message"], "This is a csv test.", "Message in the csv file is different than expected.")

    """
    Checks to see if commas in a the message field break the csv formatting.
    """
    def test_check_how_commas_in_message_field_are_handled(self):
        file_name = "test-sentinalysis-csv-commas.txt"
        file_name_csv = "test-sentinalysis-csv-commas.csv"

        with open(file_name, "w") as f1:
            f1.write("""7/24/25, 12:56 - TestPerson: This, dear TestPerson2, is a test.""")
        convert_txt_to_csv(file_name)
        os.remove(file_name)

        data = pd.read_csv(file_name_csv)
        os.remove(file_name_csv)

        self.assertEqual(data.at[0, "Message"], "This, dear TestPerson2, is a test.")
        self.assertEqual(len(data.columns), 4)

    """
    Checks whether the returned path is absolute and has the .csv file suffix.
    """
    def test_check_path_returned_by_csv_conversion_function(self):
        file_name = "test-sentinalysis-csv-abspath-check.txt"
        with open(file_name, "w") as f:
            f.write("""7/14/22, 21:09 - TestPerson: This is a test.""")
        result_path = convert_txt_to_csv(file_name)
        os.remove(file_name)

        self.assertTrue(os.path.isabs(result_path), "Returned path is not absolute.")
        self.assertTrue(result_path.endswith(".csv"), f"Returned path does not contain the '.csv' extension at the end: {result_path}")
        os.remove(result_path)

    """
    Checks if the csv conversion function throws an error when provided with an incorrect path.
    Only Windows paths are tested at the moment.
    """
    def test_provide_non_existent_path_to_csv_conversion_function(self):
        file_name1= "test-sentinalysis-non-existent-file2.txt"
        with self.assertRaises(FileNotFoundError):
            convert_txt_to_csv(file_name1)
        
        file_name2 = "C:\\Users\\username\\AppData\\Roaming\\nltk_data\\sentiment\\vader_lexicon.txt"
        with self.assertRaises(FileNotFoundError):
            convert_txt_to_csv(file_name2)

if __name__ == '__main__':
    unittest.main()