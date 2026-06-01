import unittest

from babelebab.analyze import Lexicon, analyze, tokenize_words


class TestTokenize(unittest.TestCase):
    def test_lowercases_and_drops_numbers(self):
        self.assertEqual(
            tokenize_words("The cat, 42 cats! It's fine."),
            ["the", "cat", "cats", "it", "s", "fine"],
        )

    def test_empty(self):
        self.assertEqual(tokenize_words("   "), [])


class TestLexicon(unittest.TestCase):
    def test_known_and_unknown(self):
        lex = Lexicon("eng")
        the = lex.lookup("The")
        self.assertIsNotNone(the)
        assert the is not None
        self.assertEqual(the.rank, 1)
        self.assertGreater(the.zipf, 7.0)
        self.assertIn("the", lex)
        self.assertIsNone(lex.lookup("wugglezzz"))


class TestAnalyze(unittest.TestCase):
    def test_basic_metrics(self):
        result = analyze("The cat sat on the mat. A wuggle ran.", "eng")
        self.assertEqual(result.sentence_count, 2)
        self.assertEqual(result.token_count, 9)
        self.assertEqual(result.type_count, 8)
        self.assertAlmostEqual(result.type_token_ratio, 8 / 9)
        self.assertIn("wuggle", result.unknown_words)
        self.assertGreaterEqual(result.coverage["known"], 0.5)
        self.assertTrue(0.0 < result.coverage["top1000"] <= 1.0)
        self.assertIsNotNone(result.mean_zipf)
        the = next(t for t in result.tokens if t.text == "the")
        self.assertEqual(the.rank, 1)
        self.assertTrue(the.known)

    def test_empty_and_summary(self):
        result = analyze("", "eng")
        self.assertEqual(result.token_count, 0)
        self.assertEqual(result.sentence_count, 0)
        self.assertIsNone(result.mean_zipf)
        self.assertIsInstance(result.summary(), str)


if __name__ == "__main__":
    unittest.main()
