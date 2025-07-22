from config import date_pattern, time_pattern, name_pattern, msg_pattern
from typing import Tuple 
from datetime import date

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
  msg_date, time_value, msg_sender, msg = line.split(",", 3)
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