from collections import defaultdict
from datetime import date, datetime
from dateutil import parser
from typing import Tuple 
import logging as logger
import ntpath
import time
import csv
import re
import os

# Third-party
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import numpy as np
import orjson
import ijson
import nltk

# Setup
nltk.download('vader_lexicon')

date_pattern = re.compile(r'\b\d{1,2}/\d{1,2}/\d{2}\b')
time_pattern = re.compile(r'\d{2}:\d{2}')
name_pattern = re.compile(r'(?<=- )(.*?)(?=:)')
msg_pattern = re.compile(r'(?<=: )(.*)$')

# Admin messages - useless for sentiment analysis
FILTERS = [
      "<Media omitted>",
      "changed the settings so only admins can edit the group settings",
      "changed this group's icon",
      "changed the group description",
      "pinned a message",
      "added",
      "now an admin",
      "removed",
      "no longer an admin",
      "joined using this group's invite link",
      "left",
      "changed this group's settings to allow only admins to send messages to this group",
      "started a call",
      "changed this group's settings to allow all members to send messages to this group",
      "changed the settings so all members can edit the group settings",
      "changed this group's settings to allow only admins to add others to this group",
      "turned on admin approval to join this group",
      "created group",
      "Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them. Learn more.",
      "changed their phone number to a new number. Tap to message or add the new number.",
      "was added",
      "changed to",
      "This message was deleted",
      "This group has over 256 members so now only admins can edit the group settings.",
      "New members need admin approval to join this group.",
      "As a member, you can join groups in the community and get admin updatesYour profile is visible to admins",
      "As a member, you can join groups in the community and get admin updates",
      "Your profile is visible to admins",
      "joined from the community",
      "updated the message timer. New messages will disappear from this chat 7 days after they're sent, except when kept.",
      "You received a view once message. For added privacy, you can only open it on your phone.",
]

FILTERS_REGEX = re.compile('|'.join(map(re.escape, FILTERS)))

"""
Validates the chat file line by line.
If a line has no timestamp, it's part of a multi-line message.
Therefore, the content is modified to act as one message.

Args:
  filePath (str): The path to the chat logs file, must be an exported .txt file.

Returns:
  str: The path to the validated file.
"""
def data_validation(filePath: str) -> str:
  fileName = ntpath.basename(filePath).removesuffix(".txt")
  prev_line = ""

  with open(filePath, 'r', encoding = "utf-8") as f1, open(f"validated-{fileName}.txt", 'wb+') as f2:
    for line in f1:
      if not FILTERS_REGEX.search(line):
        # If current line does not start with timestamp, treat it as message continuation
        if not date_pattern.search(line):
          prev_line = prev_line.rstrip('\n')
          prev_line += ' ' + line
        else:
          if prev_line:
            f2.write(prev_line.encode())
          prev_line = line

    # Since no message follows the last one, it has to be written at the end
    if prev_line:
      f2.write(prev_line.encode())

  return os.path.abspath(f"validated-{fileName}.txt")

"""
Convert an exported .txt file to .json format.

Args:
  filePath (str): The path to the validated chat logs file.

Returns:
  str: The path to the resulting .json file.
"""
def convert_txt_to_json(filePath: str) -> str:
  fileName = ntpath.basename(filePath).removesuffix(".txt")

  with open(filePath, 'r', encoding = "utf-8") as f1, open(f"{fileName}.json", 'w', encoding = "utf-8") as f2:
    f2.write('[\n')

    comma_flag = True
    for line in f1:
      date = date_pattern.search(line).group()
      time = time_pattern.search(line).group()
      name = name_pattern.search(line).group()
      msg = msg_pattern.search(line).group()

      # Prevents commas at the start of the file / trailing commas
      if comma_flag:
        comma_flag = False
      else:
        f2.write(",\n")

      json_str = orjson.dumps({"date":date, "message":msg, "time":time, "username":name}).decode("utf-8")
      f2.write(f'\t{json_str}')

    f2.write('\n]\n')

  return os.path.abspath(f"{fileName}.json")

"""
Convert an exported .txt file to .csv format.

Args:
  filePath (str): The path to the validated chat logs file.

Returns:
  str: The path to the resulting .csv file.
"""
def convert_txt_to_csv(filePath: str) -> str:
  fileName = ntpath.basename(filePath).removesuffix(".txt")

  with open(filePath, 'r', encoding = "utf-8") as f1, open(f"{fileName}.csv", 'w', encoding = "utf-8") as f2:
    writer = csv.writer(f2)
    writer.writerow(["Date", "Time", "Username", "Message"])

    for line in f1:
      date = date_pattern.search(line).group() # String
      time = time_pattern.search(line).group()
      name = name_pattern.search(line).group()
      msg = msg_pattern.search(line).group()

      writer.writerow([date, time, name, msg])

  return os.path.abspath(f"{fileName}.csv")

"""
Takes sentiment_analysis()'s resulting dictionary and creates a sentiment chart for each member.
Resulting directory can be downloaded.

Args:
  sentiment_dictionary (dict): A dictionary of all chat members and their sentiment scores.

Returns:
  None
"""
def get_charts(sentiment_dictionary: dict) -> None:
  os.makedirs(f"{os.getcwd()}/sentiment_chart_images/", exist_ok = True)
  directory_path = os.path.abspath("sentiment_chart_images")

  for group_member in sentiment_dictionary:
    y = np.array([score for score, _ in sentiment_dictionary[group_member]])
    x = np.array([timestamp for _, timestamp in sentiment_dictionary[group_member]])

    plt.plot(x, y)
    plt.xlabel("Dates")
    plt.ylabel("Positivity Score")
    plt.title(f"{group_member}'s positivity score")
    plt.gcf().autofmt_xdate(rotation = 45)

    plt.savefig(f"{directory_path}/{group_member}-sentiment.png", bbox_inches='tight')
    plt.close()

"""
Takes a line from a .txt file and returns the timestamp, sender, and message content.

Args:
  line (str): A line of text from the .txt file

Returns:
  Tuple(date, str, str): A tuple of all the values.
"""
def get_txt(line: str) -> Tuple[date, str, str]:
  month, day, year = map(int, date_pattern.search(line).group().split("/"))
  timestamp = date(2000 + year, month, day)
  msg_sender = name_pattern.search(line).group()
  msg = msg_pattern.search(line).group()

  return timestamp, msg_sender, msg

"""
Takes a line from a .csv file and returns the timestamp, sender, and message content.

Args:
  line (str): A line of text from the .txt file

Returns:
  Tuple(date, str, str): A tuple of all the values.
"""
def get_csv(line: str) -> Tuple[date, str, str]:
  msg_date, time, msg_sender, msg = line.split(",", 3)
  month, day, year = map(int, msg_date.split("/"))
  timestamp = date(2000 + year, month, day)
  
  return timestamp, msg_sender, msg

"""
Takes an ijson object from a .json file and returns the timestamp, sender, and message content.

Args:
  obj (dict): An ijson object from the .json file

Returns:
  Tuple(date, str, str): A tuple of all the values.
"""
def get_json(obj: str) -> Tuple[date, str, str]:
  month, day, year = map(int, obj["date"].split("/"))
  timestamp = date(2000 + year, month, day)
  msg_sender = obj["username"]
  msg = obj["message"]
  
  return timestamp, msg_sender, msg

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