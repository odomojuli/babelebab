import re


def extract_acronyms(text):
    """
    Extracts acronyms that are formatted with individual letters followed by periods 
    from the given text. For example, "U.S.A." or "N.A.T.O.".

    Pattern: \b(?:[a-zA-Z]\.){2,}
    Breakdown:
    - \b         : Asserts a word boundary, ensuring that the acronym stands alone.
    - (?:...)   : A non-capturing group.
    - [a-zA-Z]  : Matches a single alphabetical character, uppercase or lowercase.
    - \.        : Matches a literal period.
    - {2,}      : Quantifier ensuring the pattern inside the non-capturing group (i.e., a letter followed by a period) appears at least two times.

    Args:
    - text (str): The input text to search for acronyms.

    Returns:
    - list: A list of found acronyms.
    """
    pattern = r'\b(?:[a-zA-Z]\.){2,}'
    return re.findall(pattern, text)

if __name__ == "__main__":
    print(extract_acronyms("Mr."))