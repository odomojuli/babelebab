import unittest

from babelebab.detect import DetectionResult, WordlistDetector, detect


class TestDetect(unittest.TestCase):
    def test_clear_samples(self):
        cases = {
            "eng": "The quick brown fox jumps over the lazy dog and then runs away quickly.",
            "fra": "Le chat noir mange une souris dans la cuisine pendant toute la nuit.",
            "rus": "Быстрая коричневая лиса прыгает через ленивую собаку в саду.",
            "deu": "Der schnelle braune Fuchs springt über den faulen Hund im Garten.",
            "jpn": "私は毎朝コーヒーを飲みながら新聞を読みます。",
        }
        for want, text in cases.items():
            self.assertEqual(detect(text).lang, want, msg=f"{want}: {text!r}")

    def test_result_shape(self):
        result = detect("The quick brown fox jumps over the lazy dog.")
        self.assertIsInstance(result, DetectionResult)
        self.assertTrue(result.scores)
        self.assertTrue(0.0 <= result.confidence <= 1.0)
        self.assertIn("eng", result.scores)

    def test_empty_input(self):
        result = detect("   ")
        self.assertIsNone(result.lang)
        self.assertEqual(result.confidence, 0.0)
        self.assertEqual(result.scores, {})

    def test_restricted_languages(self):
        detector = WordlistDetector(langs=["eng", "fra"])
        result = detector.detect("Le chat noir mange une souris dans la cuisine.")
        self.assertEqual(result.lang, "fra")
        self.assertEqual(set(result.scores), {"eng", "fra"})


if __name__ == "__main__":
    unittest.main()
