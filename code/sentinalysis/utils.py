from nltk import data as nltk_data
from functools import lru_cache
import nltk

"""
Checks to see if the VADER lexicon is present. If not, download it.

Args:
  None

Returns:
  None
"""
@lru_cache(maxsize=None)
def check_vader_lexicon() -> None:
    try:
        nltk_data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        nltk.download('vader_lexicon', quiet = True)