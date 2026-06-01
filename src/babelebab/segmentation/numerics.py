import re


def extract_numerics(s: str) -> bool:
    """
    Determines if a given string matches the pattern ^\d*\.?\d+$

    This regex pattern breaks down as follows:
    ^       : Start of the string.
    \d*     : Matches zero or more digits (0-9).
    \.?     : Matches zero or one period (decimal point).
    \d+     : Matches one or more digits (0-9).
    $       : End of the string.

    Args:
    - s (str): The input string to check.

    Returns:
    - bool: True if the string matches the pattern, False otherwise.
    """
    pattern = r'^\d*\.?\d+$'
    return bool(re.match(pattern, s))
