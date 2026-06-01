import re


def sentence_boundary_detection(text):
    # This function will be used with re.sub to replace acronyms and numerics with unique tokens
    def replace_with_token(match, token_base, counter_dict):
        token = f"{token_base}{counter_dict[token_base]}TOKEN"
        counter_dict[token_base] += 1
        return token

    # Counters to ensure each substitution has a unique token
    counters = {"ACRONYM": 0, "NUMERIC": 0}

    # 1. Scan for acronyms and substitute them
    acronym_pattern = r'\b(?:[a-zA-Z]\.){2,}'
    text = re.sub(acronym_pattern, lambda match: replace_with_token(match, "ACRONYM", counters), text)

    # 2. Scan for numerics and substitute them
    numeric_pattern = r'\d*\.?\d+'
    text = re.sub(numeric_pattern, lambda match: replace_with_token(match, "NUMERIC", counters), text)

    # 3. Split the text on known delimiters
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # 4. Restore original acronyms and numerics from the special tokens
    acronym_matches = re.findall(acronym_pattern, text)
    for i, acronym in enumerate(acronym_matches):
        token = f"ACRONYM{i}TOKEN"
        sentences = [sentence.replace(token, acronym) for sentence in sentences]
        
    numeric_matches = re.findall(numeric_pattern, text)
    for i, numeric in enumerate(numeric_matches):
        token = f"NUMERIC{i}TOKEN"
        sentences = [sentence.replace(token, numeric) for sentence in sentences]

    return sentences

if __name__ == "__main__":
    text = "The U.S. and E.U. have a GDP of 2.5 and 3.8 trillion respectively! What do you think? Dr. Smith agrees. Also, the value is 5."
    for sentence in sentence_boundary_detection(text):
        print(sentence)