from sentinalysis.validation import data_validation
import unittest
import fnmatch
import filecmp
import os

class TestValidation(unittest.TestCase):
    """
    Checks if the input file contains admin messages after validation process.
    """
    def test_remove_admin_messages_during_validation(self):
        file_name = "sentinalysis-validation-function-check.txt"
        admin_message = "TestPerson changed the settings so only admins can edit the group settings"

        with open(file_name, "w") as f1:
            f1.write(f"""7/23/25, 16:45 - TestPerson: This is a test.\n{admin_message}""")
        
        result_file = data_validation(file_name, os.getcwd())
        with open(result_file, 'r') as f2:
            data = f2.read()

        os.remove(file_name)
        os.remove(result_file)
        self.assertNotIn(admin_message, data, "Unexpected admin message found in validated file.")

    def test_properly_concatenate_message_continuation_into_message(self):
        file_name = "sentinalysis-validation-multi-line-message.txt"

        with open(file_name, 'w') as f1:
            f1.write("""7/23/25, 16:45 - TestPerson: This is a test.\nAnd it also happens to be a multi-line message.""")
        
        result_file = data_validation(file_name, os.getcwd())
        with open(result_file, 'r') as f2:
            data = f2.read()

        with open(result_file, "rb") as f3:
            num_lines = sum(1 for _ in f3)
        
        os.remove(file_name)
        os.remove(result_file)
        self.assertEqual(num_lines, 1, "The multi-line message merging did not go as expected.")
        self.assertIn("This is a test. And it also happens to be a multi-line message.", data)

    """
    Checks to see if the last line is properly validated, even without a trailing newline character.
    """
    def test_last_message_no_newline(self):
        file_name = "sentinalysis-no-newline.txt"

        with open(file_name, 'w') as f1:
            f1.write("""8/1/25, 14:49 - TestPerson1: This is a test.\n8/1/25, 14:50 - TestPerson2: This is another test.""")
        
        result_file = data_validation(file_name, os.getcwd())
        with open(result_file, 'r') as f2:
            data = f2.read()
        
        os.remove(file_name)
        os.remove(result_file)
        self.assertEqual(data.split('\n')[1], "8/1/25, 14:50 - TestPerson2: This is another test.", "The validated line is different from the expected output.")

    """
    Checks if the validated file:
        - The file exists
        - The returned path is absolute
        - Contains the "validated-" substring in its name
    """
    def test_return_value(self):
        file_name = "sentinalysis-return-value.txt"

        with open(file_name, 'w') as f1:
            f1.write("""8/1/25, 15:01 - TestPerson1: This is a test.""")
        
        result_file = data_validation(file_name, os.getcwd())

        self.assertTrue(os.path.isfile(result_file), "The file does not exist.")
        self.assertTrue(os.path.isabs(result_file), "The returned path is not absolute.")
        
        self.assertTrue(fnmatch.fnmatch(result_file, '*validated-*'), 'the validated file does not contain the "validated-" substring in its file name.')
        
        os.remove(file_name)
        os.remove(result_file)
    
    """
    Checks to see if double validation returns something different. 
    The expectation is that no matter the amount of validations, the output is the same.
    """
    def test_double_validation_should_return_identical_results(self):
        file_name = "sentinalysis-double-validation.txt"

        with open(file_name, 'w') as f1:
            f1.write("""8/1/25, 15:23 - TestPerson: This is a test.""")
        
        result_file = data_validation(file_name, os.getcwd())
        double_result_file = data_validation(result_file, os.getcwd())

        self.assertTrue(filecmp.cmp(result_file, double_result_file), "Multiple validations of the same file returned different outputs.")

        os.remove(file_name)
        os.remove(result_file)
        os.remove(double_result_file)

    """
    Checks if special characters are modified by the validation process.
    """
    def test_special_characters_not_modified(self):
        non_ascii = "漢"
        emoji = "💀"
        accented_n = "ñ"
        copyright_symbol = "©"

        checklist = [non_ascii, emoji, accented_n, copyright_symbol]

        file_name = "sentinalysis-special-characters.txt"

        with open(file_name, 'w', encoding="utf-8") as f1:
            f1.write(f"""8/1/25, 15:23 - TestPerson: {non_ascii}{emoji}{accented_n}{copyright_symbol}""")
        
        result_file = data_validation(file_name, os.getcwd())
        with open(result_file, 'r', encoding="utf-8") as f2:
            data = f2.read()

        data = data.split(': ')[1]

        for idx, _ in enumerate(data):
            self.assertEqual(checklist[idx], data[idx], "Special character is different than expected.")
        
        os.remove(file_name)
        os.remove(result_file)

    """
    Checks that missing source files raise "FileNotFoundError".
    """
    def test_check_if_missing_source_file_returns_error(self):
        file_name1 = "sentinalysis-non-existent-file.txt"
        with self.assertRaises(FileNotFoundError):
            data_validation(file_name1, os.getcwd())

        file_name2 = "C:\\Users\\username\\AppData\\Roaming\\nltk_data\\sentiment\\vader_lexicon.txt"
        with self.assertRaises(FileNotFoundError):
            data_validation(file_name2, os.getcwd())
