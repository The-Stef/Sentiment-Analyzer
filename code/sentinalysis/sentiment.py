from nltk.sentiment.vader import SentimentIntensityAnalyzer
from .parsers import get_txt, get_json, get_csv
from .utils import check_vader_lexicon
from collections import defaultdict
import ijson
import os

def update_user_sentiment_score(analyzer, msg, members_sentiment, members_sentiment_cache, name, timestamp):
  score = analyzer.polarity_scores(msg)["compound"]

  new_sentiment_value = members_sentiment_cache.get(name, 0.0) + score

  members_sentiment[name].append((new_sentiment_value, timestamp))
  members_sentiment_cache[name] = new_sentiment_value

"""
Analyzes all messages in a file to calculate sentiment scores.
Currently supports: .txt, .json, .csv

Args:
  filePath (str): The path to the file.

Returns:
  dict: A dictionary of all chat members and their sentiment scores.
"""
def sentiment_analysis(filePath: str) -> dict:
  fileExtension = os.path.splitext(filePath)[1].lower()
  members_sentiment = defaultdict(list)
  members_sentiment_cache = {}
  check_vader_lexicon()
  analyzer = SentimentIntensityAnalyzer()

  if fileExtension == ".csv":
    with open(filePath, "r", encoding = "utf-8") as f:
      next(f)
      for line in f:
        timestamp, msg_sender, msg = get_csv(line)
        update_user_sentiment_score(analyzer, msg, members_sentiment, members_sentiment_cache, msg_sender, timestamp)
  elif fileExtension == ".json":
    with open(filePath, "rb") as f:
      for obj in ijson.items(f, "item"):
        timestamp, msg_sender, msg = get_json(obj)
        update_user_sentiment_score(analyzer, msg, members_sentiment, members_sentiment_cache, msg_sender, timestamp)
  elif fileExtension == ".txt":
    with open(filePath, "r", encoding = "utf-8") as f:
      for line in f:
        timestamp, msg_sender, msg = get_txt(line)
        update_user_sentiment_score(analyzer, msg, members_sentiment, members_sentiment_cache, msg_sender, timestamp)
  else:
    raise ValueError(f"Unsupported file extension: {fileExtension}")

  return members_sentiment