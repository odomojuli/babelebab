import csv
import tempfile
import unittest
from pathlib import Path

from babelebab.analyze import Lemmatizer, Lexicon, analyze, simplemma_available


def _make_lexicon(rows: list[tuple[str, float, float]]) -> Lexicon:
    root = Path(tempfile.mkdtemp())
    lang_dir = root / "tst"
    lang_dir.mkdir()
    with (lang_dir / "tst_wordfreq_top10.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["rank", "word", "freq_per_million", "zipf"])
        for rank, (word, fpm, zipf) in enumerate(rows, start=1):
            writer.writerow([rank, word, fpm, zipf])
    return Lexicon("tst", wordlists_root=root)


class TestLemmatizer(unittest.TestCase):
    def test_unsupported_language_is_noop(self):
        self.assertEqual(Lemmatizer()("foo", "jpn"), "foo")

    @unittest.skipUnless(simplemma_available(), "simplemma not installed")
    def test_real_english_lemma(self):
        lem = Lemmatizer()
        self.assertEqual(lem("jumps", "eng"), "jump")
        self.assertEqual(lem("mice", "eng"), "mouse")


class TestAnalyzeLemmatization(unittest.TestCase):
    def setUp(self):
        self.lex = _make_lexicon([("the", 50000, 7.7), ("cat", 500, 5.7), ("jump", 100, 5.0)])

    def test_injected_lemmatizer_resolves_surface_miss(self):
        def stub(word: str, lang: str) -> str:
            return {"jumps": "jump"}.get(word, word)

        result = analyze("The cat jumps.", "tst", lexicon=self.lex, lemmatizer=stub)
        self.assertNotIn("jumps", result.unknown_words)
        token = next(t for t in result.tokens if t.text == "jumps")
        self.assertTrue(token.known)
        self.assertEqual(token.lemma, "jump")
        self.assertEqual(token.rank, 3)

    def test_lemmatize_false_keeps_surface_unknown(self):
        result = analyze("The cat jumps.", "tst", lexicon=self.lex, lemmatize=False)
        self.assertIn("jumps", result.unknown_words)
        token = next(t for t in result.tokens if t.text == "jumps")
        self.assertFalse(token.known)
        self.assertIsNone(token.lemma)


if __name__ == "__main__":
    unittest.main()
