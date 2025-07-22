import matplotlib.pyplot as plt
import numpy as np
import os

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