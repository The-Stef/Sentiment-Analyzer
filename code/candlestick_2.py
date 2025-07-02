# Standard Library
from collections import defaultdict
from datetime import date, datetime
from dateutil import parser
import logging as logger
import ntpath
import time
import re
import os

# Third-party
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import numpy as np
import nltk

# Setup
nltk.download('vader_lexicon')

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
  date_pattern = re.compile(r'\b\d{1,2}/\d{1,2}/\d{2}, \d{2}:\d{2}\b')
  prev_line = ""

  with open(filePath, 'r') as f1, open(f"validated-{fileName}.txt", 'wb+') as f2:
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
Analyzes all messages in a text file to calculate sentiment scores.

Args:
  filePath (str): The path to the validated chat logs file.

Returns:
  dict: A dictionary of all chat members and their sentiment scores.
"""
def sentiment_analysis(filePath: str) -> dict:
  members_sentiment = defaultdict(list)
  members_sentiment_cache = {}
  analyzer = SentimentIntensityAnalyzer()

  date_pattern = re.compile(r'\b\d{1,2}/\d{1,2}/\d{2}\b')
  name_pattern = re.compile(r'(?<=- )(.*?)(?=:)')
  msg_pattern = re.compile(r'(?<=: )(.*)$')

  with open(filePath, 'r') as f:
    for line in f:
      # Get message components
      month, day, year = map(int, date_pattern.search(line).group().split("/"))
      timestamp = date(2000 + year, month, day)
      msg_sender = name_pattern.search(line).group()
      msg = msg_pattern.search(line).group()

      # Acquire compounded sentiment score
      score = analyzer.polarity_scores(msg)["compound"]

      new_sentiment_value = members_sentiment_cache.get(msg_sender, 0.0) + score

      members_sentiment[msg_sender].append((new_sentiment_value, timestamp))
      members_sentiment_cache[msg_sender] = new_sentiment_value

  return members_sentiment

"""
Convert an exported .txt file to .json format.

Args:
  filePath (str): The path to the validated chat logs file.

Returns:
  str: The path to the resulting .json file.
"""
def convert_txt_to_json(filePath: str) -> str:
  fileName = ntpath.basename(filePath).removesuffix(".txt")

  date_pattern = re.compile(r'\b\d{1,2}/\d{1,2}/\d{2}\b')
  time_pattern = re.compile(r'\d{2}:\d{2}')
  name_pattern = re.compile(r'(?<=- )(.*?)(?=:)')
  msg_pattern = re.compile(r'(?<=: )(.*)$')

  with open(filePath, 'r') as f1, open(f"{fileName}.json", 'w', encoding = "utf-8") as f2:
    f2.write('{\n\t"conversation": [\n')

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
      f2.write(f'\t\t{json_str}')
    
    f2.write('\n\t]\n}\n')

  return os.path.abspath(f"{fileName}.json")

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