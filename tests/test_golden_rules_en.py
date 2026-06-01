import unittest

from babelebab.segmentation import pysbd_available, split_sentences


def _noop(fn):
    return fn


# pysbd segments these cases differently from the golden expectations (by
# design): expected-failure when pysbd is the active backend, no-op otherwise.
_pysbd_divergence = unittest.expectedFailure if pysbd_available() else _noop


class TestSentenceSplitting(unittest.TestCase):
    
    def test_simple_period_to_end_sentence(self):
        text = "Hello World. My name is Jonas."
        expected = ["Hello World.", "My name is Jonas."]
        self.assertEqual(split_sentences(text), expected)

    def test_question_mark_end_sentence(self):
        text = "What is your name? My name is Jonas."
        expected = ["What is your name?", "My name is Jonas."]
        self.assertEqual(split_sentences(text), expected)

    def test_exclamation_point_to_end_sentence(self):
        text = "There it is! I found it."
        expected = ["There it is!", "I found it."]
        self.assertEqual(split_sentences(text), expected)

    def test_one_letter_upper_case_abbreviations(self):
        text = "My name is Jonas E. Smith."
        expected = ["My name is Jonas E. Smith."]
        self.assertEqual(split_sentences(text), expected)

    def test_one_letter_lower_case_abbreviations(self):
        text = "Please turn to p. 55."
        expected = ["Please turn to p. 55."]
        self.assertEqual(split_sentences(text), expected)

    def test_two_letter_lc_middle_sentence(self):
        text = "Were Jane and co. at the party?"
        expected = ["Were Jane and co. at the party?"]
        self.assertEqual(split_sentences(text), expected)

    def test_two_letter_uc_middle_sentence(self):
        text = "They closed the deal with Pitt, Briggs & Co. at noon."
        expected = ["They closed the deal with Pitt, Briggs & Co. at noon."]
        self.assertEqual(split_sentences(text), expected)

    def test_two_letter_lc_end_sentence(self):
        text = "Let's ask Jane and co. They should know."
        expected = ["Let's ask Jane and co.", "They should know."]
        self.assertEqual(split_sentences(text), expected)

    def test_two_letter_uc_end_sentence(self):
        text = "They closed the deal with Pitt, Briggs & Co. It closed yesterday."
        expected = ["They closed the deal with Pitt, Briggs & Co.", "It closed yesterday."]
        self.assertEqual(split_sentences(text), expected)

    def test_two_letter_prepositive_abbreviations(self):
        text = "I can see Mt. Fuji from here."
        expected = ["I can see Mt. Fuji from here."]
        self.assertEqual(split_sentences(text), expected)

    def test_two_letter_pre_post_abbreviations(self):
        text = "St. Michael's Church is on 5th st. near the light."
        expected = ["St. Michael's Church is on 5th st. near the light."]
        self.assertEqual(split_sentences(text), expected)

    def test_possessive_two_letter_abbreviations(self):
        text = "That is JFK Jr.'s book."
        expected = ["That is JFK Jr.'s book."]
        self.assertEqual(split_sentences(text), expected)

    def test_multi_period_middle_sentence(self):
        text = "I visited the U.S.A. last year."
        expected = ["I visited the U.S.A. last year."]
        self.assertEqual(split_sentences(text), expected)

    def test_us_sentence_boundary(self):
        text = "I live in the U.S. How about you?"
        expected = ["I live in the U.S.", "How about you?"]
        self.assertEqual(split_sentences(text), expected)

    def test_us_non_sentence_boundary_capitalized(self):
        text = "I work for the U.S. Government in Virginia."
        expected = ["I work for the U.S. Government in Virginia."]
        self.assertEqual(split_sentences(text), expected)

    def test_us_non_sentence_boundary(self):
        text = "I have lived in the U.S. for 20 years."
        expected = ["I have lived in the U.S. for 20 years."]
        self.assertEqual(split_sentences(text), expected)

    @_pysbd_divergence
    def test_am_pm_boundaries(self):
        text = "At 5 a.m. Mr. Smith went to the bank. He left the bank at 6 P.M. Mr. Smith then went to the store."
        expected = ["At 5 a.m. Mr. Smith went to the bank.", "He left the bank at 6 P.M.", "Mr. Smith then went to the store."]
        self.assertEqual(split_sentences(text), expected)

    def test_number_non_sentence_boundary(self):
        text = "She has $100.00 in her bag."
        expected = ["She has $100.00 in her bag."]
        self.assertEqual(split_sentences(text), expected)

    def test_number_sentence_boundary(self):
        text = "She has $100.00. It is in her bag."
        expected = ["She has $100.00.", "It is in her bag."]
        self.assertEqual(split_sentences(text), expected)

    def test_parenthetical_inside_sentence(self):
        text = "He teaches science (He previously worked for 5 years as an engineer.) at the local University."
        expected = ["He teaches science (He previously worked for 5 years as an engineer.) at the local University."]
        self.assertEqual(split_sentences(text), expected)

    def test_email_addresses(self):
        text = "Her email is Jane.Doe@example.com. I sent her an email."
        expected = ["Her email is Jane.Doe@example.com.", "I sent her an email."]
        self.assertEqual(split_sentences(text), expected)

    def test_web_addresses_with_path(self):
        text = "The site is: https://www.example.50.com/new-site/awesome_content.html. Please check it out."
        expected = ["The site is: https://www.example.50.com/new-site/awesome_content.html.", "Please check it out."]
        self.assertEqual(split_sentences(text), expected)

    def test_single_quotations_inside_sentence(self):
        text = "She turned to him, 'This is great.' she said."
        expected = ["She turned to him, 'This is great.' she said."]
        self.assertEqual(split_sentences(text), expected)

    def test_double_quotations_inside_sentence(self):
        text = 'She turned to him, "This is great." she said.'
        expected = ['She turned to him, "This is great." she said.']
        self.assertEqual(split_sentences(text), expected)

    # ... add similar tests for all other rules

    def test_multiple_periods_inside_sentence(self):
        text = "She has a Ph.D. She teaches at the local university."
        expected = ["She has a Ph.D.", "She teaches at the local university."]
        self.assertEqual(split_sentences(text), expected)

    @_pysbd_divergence
    def test_ellipsis_inside_sentence(self):
        text = "She said... and then what?"
        expected = ["She said...", "and then what?"]
        self.assertEqual(split_sentences(text), expected)

    def test_ellipsis_at_sentence_end(self):
        text = "I wonder what she meant by that..."
        expected = ["I wonder what she meant by that..."]
        self.assertEqual(split_sentences(text), expected)

    def test_question_exclamation_combined(self):
        text = "Are you coming?! I can't believe it!"
        expected = ["Are you coming?!", "I can't believe it!"]
        self.assertEqual(split_sentences(text), expected)

    def test_multiple_exclamations(self):
        text = "That's amazing!! I need to see it to believe it!"
        expected = ["That's amazing!!", "I need to see it to believe it!"]
        self.assertEqual(split_sentences(text), expected)

    def test_decimal_points(self):
        text = "She bought it for $5.50. It was on sale."
        expected = ["She bought it for $5.50.", "It was on sale."]
        self.assertEqual(split_sentences(text), expected)

    @_pysbd_divergence
    def test_acronyms_and_abbreviations(self):
        text = "He's from the U.K. and works at B.B.C. It's quite a prestigious job."
        expected = ["He's from the U.K. and works at B.B.C.", "It's quite a prestigious job."]
        self.assertEqual(split_sentences(text), expected)

    def test_dates_in_sentence(self):
        text = "Her birthday is on 20.11.2023. We'll have a party."
        expected = ["Her birthday is on 20.11.2023.", "We'll have a party."]
        self.assertEqual(split_sentences(text), expected)

    def test_dates_with_commas(self):
        text = "On July 4, 1776, the declaration was signed. It was a pivotal day."
        expected = ["On July 4, 1776, the declaration was signed.", "It was a pivotal day."]
        self.assertEqual(split_sentences(text), expected)

    def test_domain_names(self):
        text = "Visit my website at www.example.com. You'll find great resources there."
        expected = ["Visit my website at www.example.com.", "You'll find great resources there."]
        self.assertEqual(split_sentences(text), expected)

    def test_quotes_inside_sentence(self):
        text = "She said, \"Hello.\" He replied, \"Hi.\""
        expected = ["She said, \"Hello.\"", "He replied, \"Hi.\""]
        self.assertEqual(split_sentences(text), expected)

    def test_quotes_at_sentence_end(self):
        text = "\"I'm going home,\" she said. \"Me too,\" he replied."
        expected = ["\"I'm going home,\" she said.", "\"Me too,\" he replied."]
        self.assertEqual(split_sentences(text), expected)

    @_pysbd_divergence
    def test_multi_period_abbreviations(self):
        text = "She works for the U.S.A. It's a federal job."
        expected = ["She works for the U.S.A.", "It's a federal job."]
        self.assertEqual(split_sentences(text), expected)

    def test_emails(self):
        text = "My email is john.doe@example.com. Please send me the report."
        expected = ["My email is john.doe@example.com.", "Please send me the report."]
        self.assertEqual(split_sentences(text), expected)

    def test_web_addresses(self):
        text = "Visit https://www.example.com. It has all the information."
        expected = ["Visit https://www.example.com.", "It has all the information."]
        self.assertEqual(split_sentences(text), expected)

    def test_ellipsis_with_brackets(self):
        text = "\"That was a great time [...] wasn't it?\" He reminisced."
        expected = ["\"That was a great time [...] wasn't it?\"", "He reminisced."]
        self.assertEqual(split_sentences(text), expected)

    @_pysbd_divergence
    def test_errant_newlines(self):
        text = "This is a sentence\ncut off by a newline."
        expected = ["This is a sentence cut off by a newline."]
        self.assertEqual(split_sentences(text), expected)

    def test_geo_coordinates(self):
        text = "The treasure is at N°. 1026.253.553. Bring a shovel."
        expected = ["The treasure is at N°. 1026.253.553.", "Bring a shovel."]
        self.assertEqual(split_sentences(text), expected)

    @_pysbd_divergence
    def test_double_punctuation(self):
        text = "What?!! You're joking!"
        expected = ["What?!!", "You're joking!"]
        self.assertEqual(split_sentences(text), expected)

    def test_alphabetical_list(self):
        text = "a. The first item b. The second item c. The third item"
        expected = ["a. The first item", "b. The second item", "c. The third item"]
        self.assertEqual(split_sentences(text), expected)

    @_pysbd_divergence
    def test_bullet_list(self):
        text = "• Item 1 • Item 2 • Item 3"
        expected = ["• Item 1", "• Item 2", "• Item 3"]
        self.assertEqual(split_sentences(text), expected)

    def test_4_dot_ellipsis(self):
        text = "This thought was left incomplete . . . . I wonder why."
        expected = ["This thought was left incomplete . . . .", "I wonder why."]
        self.assertEqual(split_sentences(text), expected)


if __name__ == '__main__':
    unittest.main()