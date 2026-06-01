import unittest

from babelebab.translate import (
    IdentityEngine,
    ReplayEngine,
    available,
    best_pick,
    compare,
    get,
    register,
    translate,
    unregister,
)


class TestTranslateHub(unittest.TestCase):
    def setUp(self):
        for name in list(available()):
            unregister(name)

    def test_identity_engine_roundtrip(self):
        result = translate("Hello world.", "eng", "fra", engine=IdentityEngine())
        self.assertEqual(result.text, "Hello world.")
        self.assertEqual(result.engine, "identity")
        self.assertEqual(result.tgt_lang, "fra")

    def test_registry_get_missing_raises(self):
        with self.assertRaises(KeyError):
            get("does-not-exist")

    def test_replay_known_words(self):
        deepl = ReplayEngine("DEEPL")
        self.assertEqual(deepl.translate("she", "eng", "fra").text, "elle")
        self.assertEqual(deepl.translate("do", "eng", "fra").text, "faire")

    def test_replay_unknown_word_raises(self):
        deepl = ReplayEngine("DEEPL")
        with self.assertRaises(KeyError):
            deepl.translate("zzzznotaword", "eng", "fra")

    def test_compare_collects_and_skips(self):
        register(ReplayEngine("DEEPL"))
        register(ReplayEngine("AMAZON"))
        results = compare("she", "eng", "fra")
        self.assertEqual(len(results), 2)
        self.assertEqual({r.text for r in results}, {"elle"})
        # a word no engine has -> all skipped -> empty
        self.assertEqual(compare("zzzznotaword", "eng", "fra"), [])

    def test_best_pick_consensus(self):
        register(ReplayEngine("DEEPL"))
        register(ReplayEngine("AMAZON"))
        best = best_pick("she", "eng", "fra")
        self.assertIsNotNone(best)
        assert best is not None
        self.assertEqual(best.text, "elle")
        self.assertEqual(best.engine, "best_pick")
        self.assertEqual(best.meta["strategy"], "consensus")

    def test_best_pick_no_engines_returns_none(self):
        self.assertIsNone(best_pick("she", "eng", "fra", engines=[]))


if __name__ == "__main__":
    unittest.main()
