import unittest

from babelebab import PipelineResult, pipeline
from babelebab.translate import IdentityEngine


class TestPipeline(unittest.TestCase):
    def test_detect_and_analyze(self):
        text = "The quick brown fox jumps over the lazy dog. It then runs away quickly."
        result = pipeline(text)
        self.assertIsInstance(result, PipelineResult)
        self.assertEqual(result.src_lang, "eng")
        self.assertIsNotNone(result.detection)
        self.assertEqual(len(result.sentences), 2)
        self.assertIsNotNone(result.analysis)
        self.assertEqual(result.analysis.lang, "eng")
        self.assertIsNone(result.translated_text)

    def test_src_lang_override_skips_detection(self):
        result = pipeline("Hello world. Goodbye now.", src_lang="eng")
        self.assertIsNone(result.detection)
        self.assertEqual(result.src_lang, "eng")
        self.assertIsNotNone(result.analysis)

    def test_translation_with_identity_engine(self):
        text = "Hello world. Goodbye now."
        result = pipeline(text, src_lang="eng", translate_to="fra", engine=IdentityEngine())
        self.assertEqual(result.tgt_lang, "fra")
        self.assertEqual(len(result.translations), len(result.sentences))
        self.assertEqual(result.translated_text, " ".join(result.sentences))

    def test_missing_wordlist_analysis_is_none(self):
        result = pipeline("whatever text goes here", src_lang="zza")
        self.assertIsNone(result.analysis)
        self.assertEqual(result.src_lang, "zza")


if __name__ == "__main__":
    unittest.main()
