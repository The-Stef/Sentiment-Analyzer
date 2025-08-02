from sentinalysis.sentiment import update_user_sentiment_score, sentiment_analysis
from sentinalysis.utils import check_vader_lexicon
from unittest.mock import Mock, patch
from datetime import date
import unittest
import os

class TestSentiment(unittest.TestCase):
    """
    Checks to see if the update_user_sentiment_score() function works as intended.
    """
    def test_update_sentiment_score_function(self):
        mocked_analyzer = Mock()
        mocked_analyzer.polarity_scores.return_value = {"compound": 0.5}

        msg = "Such a great test!"
        dict_scores = {"Stef": []}
        dict_scores_cache = {"Stef": 1.0}
        name = "Stef"
        timestamp = date(2025, 8, 1)

        update_user_sentiment_score(mocked_analyzer, msg, dict_scores, dict_scores_cache, name, timestamp)

        self.assertEqual(dict_scores["Stef"], [(1.5, timestamp)], "The sentiment score tuple is different than expected.")
        self.assertEqual(dict_scores_cache["Stef"], 1.5, "The actual cache value does not coincide with the expected one.")

    """
    Checks to see if the sentiment scores of one user don't affect the sentiment scores of different users.
    """
    def test_check_if_sentiment_scores_of_one_person_dont_affect_other_person(self):
        mocked_analyzer = Mock()
        mocked_analyzer.polarity_scores.return_value = {"compound": 0.5}

        msg = "Such a great test!"
        dict_scores = {"Stef": [], "NotStef": [(0.6, date(2025, 7, 31))]}
        dict_scores_cache = {"Stef": 1.2, "NotStef": 0.6}
        name = "Stef"
        timestamp = date(2025, 8, 1)

        update_user_sentiment_score(mocked_analyzer, msg, dict_scores, dict_scores_cache, name, timestamp)

        self.assertEqual(len(dict_scores["Stef"]), 1, "There are more elements in the list than expected.")

        self.assertEqual(dict_scores["Stef"], [(1.7, date(2025, 8, 1))], "The updated sentiment score tuple is different than expected.")
        self.assertEqual(dict_scores["NotStef"], [(0.6, date(2025, 7, 31))], "The tuple was modified, although it should not have been.")

        self.assertEqual(dict_scores_cache["Stef"], 1.7, "The cache value differs from the expected value.")
        self.assertEqual(dict_scores_cache["NotStef"], 0.6, "The cache value was modified, although it should not have been.")

    """
    Checks to see if providing a negative value subtracts from the last value instead of adding to it.
    """
    def test_check_that_negative_scores_subtract_from_total(self):
        mocked_analyzer = Mock()
        mocked_analyzer.polarity_scores.return_value = {"compound": -0.5}

        msg = "Such a bad test!"
        dict_scores = {"Stef": []}
        dict_scores_cache = {"Stef": 1.0}
        name = "Stef"
        timestamp = date(2025, 8, 1)

        update_user_sentiment_score(mocked_analyzer, msg, dict_scores, dict_scores_cache, name, timestamp)

        self.assertEqual(dict_scores["Stef"], [(0.5, timestamp)], "The sentiment score tuple is different than expected.")
        self.assertEqual(dict_scores_cache["Stef"], 0.5)

    """
    Checks to see if an empty file returns an empty dictionary.
    An empty dictionary is evaluated as False when converted to bool, therefore we use assertFalse.
    """
    def test_check_if_empty_file_returns_empty_dictionary(self):
        test_file = "sentinalysis-empty-file.txt"
        open(test_file, 'a').close()

        result_dict = sentiment_analysis(test_file)

        self.assertFalse(bool(result_dict), "The dictionary is not empty.")
        os.remove(test_file)

    """
    Checks to see if the check_vader_lexicon() function inside sentiment_analysis() is only called once.
    """
    def test_lexicon_function_is_invoked_once(self):
        check_vader_lexicon.cache_clear()
        test_file = "sentinalysis-empty-file.txt"
        open(test_file, 'a').close()

        with patch("sentinalysis.sentiment.check_vader_lexicon", wraps = check_vader_lexicon) as spy_check:
            sentiment_analysis(test_file)
            spy_check.assert_called_once()
        
        os.remove(test_file)

    """
    Checks to see that providing an unsupported file type (such as markdown / .md) returns a ValueError.
    """
    def test_provide_sentiment_analysis_function_with_unsupported_file_type(self):
        test_file = "sentinalysis-markdown.md"

        with self.assertRaises(ValueError):
            sentiment_analysis(os.path.join(os.getcwd(), test_file))

    def test_main_sentiment_analysis_function(self):
        mocked_analyzer = Mock()
        mocked_analyzer.polarity_scores.return_value = {"compound": 0.5}

        test_file_txt = "sentinalysis-function-1.txt"
        test_file_csv = "sentinalysis-function-2.csv"
        test_file_json = "sentinalysis-function-3.json"

        with open(test_file_txt, 'w') as f1:
            f1.write("""8/2/25, 18:32 - TestPerson: This is a test.""")

        with open(test_file_csv, 'w') as f2:
            f2.write("""Date,Time,Username,Message\n8/2/25,18:32,TestPerson,This is a test.""")

        with open(test_file_json, 'w') as f3:
            f3.write("""[{"date":"8/2/25","message":"This is a test.","time":"18:32","username":"TestPerson"}]""")

        with patch("sentinalysis.sentiment.SentimentIntensityAnalyzer", return_value = mocked_analyzer):
            from sentinalysis.sentiment import sentiment_analysis

            dict_txt = sentiment_analysis(test_file_txt)
            dict_csv = sentiment_analysis(test_file_csv)
            dict_json = sentiment_analysis (test_file_json)

        self.assertEqual(dict_txt["TestPerson"], [(0.5, date(2025, 8, 2))])
        self.assertEqual(dict_csv["TestPerson"], [(0.5, date(2025, 8, 2))])
        self.assertEqual(dict_json["TestPerson"], [(0.5, date(2025, 8, 2))])

        os.remove(test_file_txt)
        os.remove(test_file_csv)
        os.remove(test_file_json)

if __name__ == "__main__":
    unittest.main()