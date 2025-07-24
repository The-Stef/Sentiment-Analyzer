from sentinalysis.validation import data_validation
import unittest
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
        
