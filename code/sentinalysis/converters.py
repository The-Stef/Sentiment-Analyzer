from .config import date_pattern, time_pattern, name_pattern, msg_pattern
import ntpath
import orjson
import csv
import os

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