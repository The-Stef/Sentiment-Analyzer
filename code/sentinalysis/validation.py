from .config import FILTERS_REGEX, date_pattern
import ntpath
import os

"""
Validates the chat file line by line.
If a line has no timestamp, it's part of a multi-line message.
Therefore, the content is modified to act as one message.

Args:
  filePath (str): The path to the chat logs file, must be an exported .txt file.
  outputPath (str): The path of the directory where the validated .txt file will be saved.

Returns:
  str: The path to the validated file.
"""
def data_validation(filePath: str, outputPath: str) -> str:
  fileName = ntpath.basename(filePath).removesuffix(".txt")
  outputPath = os.path.join(outputPath, f"validated-{fileName}.txt")
  prev_line = ""

  with open(filePath, 'r', encoding = "utf-8") as f1, open(outputPath, 'wb+') as f2:
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

  return os.path.abspath(outputPath)