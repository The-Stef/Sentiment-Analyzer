from sentinalysis.converters import convert_txt_to_json
import unittest
import json
import os

class TestConverters(unittest.TestCase):
    """
    Checks if the convert_txt_to_json function behaves properly.
    Converts validated .txt input to .json, and checks whether the JSON object components contain the proper information.
    """
    def test_correct_conversion_to_json_file(self):
        fileName = "test-sentinalysis-json-conversion.txt"
        fileNameJson = "test-sentinalysis-json-conversion.json"

        with open(fileName, "w") as f1:
            f1.write("""7/23/25, 16:45 - TestPerson: This is a test.""")
        converted_json = convert_txt_to_json(fileName)
        os.remove(fileName)

        with open(converted_json, "r") as f2:
            data = json.load(f2)
        os.remove(fileNameJson)

        self.assertEqual(data[0]["date"], "7/23/25")
        self.assertEqual(data[0]["message"], "This is a test.")
        self.assertEqual(data[0]["time"], "16:45")
        self.assertEqual(data[0]["username"], "TestPerson")


if __name__ == '__main__':
    unittest.main()