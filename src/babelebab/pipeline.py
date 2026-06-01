"""End-to-end pipeline: detect -> segment -> analyze (+ optional translate).

A thin orchestrator over the stage packages; see docs/specs/0005-pipeline.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .analyze import AnalysisResult, Lexicon, analyze
from .detect import DetectionResult, Detector
from .detect import detect as detect_language
from .segmentation import split_sentences
from .translate import Engine, TranslationResult


@dataclass
class PipelineResult:
    text: str
    src_lang: str | None
    detection: DetectionResult | None
    sentences: list[str]
    analysis: AnalysisResult | None
    tgt_lang: str | None = None
    translations: list[TranslationResult] = field(default_factory=list)
    translated_text: str | None = None

    def summary(self) -> str:
        parts = [f"src={self.src_lang}", f"{len(self.sentences)} sentence(s)"]
        if self.analysis is not None:
            parts.append(f"{self.analysis.coverage.get('known', 0.0):.0%} known")
        if self.translated_text is not None:
            parts.append(f"-> {self.tgt_lang}")
        return "pipeline: " + ", ".join(parts)


def pipeline(
    text: str,
    *,
    src_lang: str | None = None,
    detector: Detector | None = None,
    analyze_text: bool = True,
    lexicon: Lexicon | None = None,
    translate_to: str | None = None,
    engine: Engine | None = None,
) -> PipelineResult:
    """Run ``text`` through detect -> segment -> analyze, optionally translating.

    Detection is skipped when ``src_lang`` is given. Analysis is skipped (returns
    ``None``) when the language has no wordlist. Translation runs only when both
    ``translate_to`` and ``engine`` are supplied, sentence by sentence.
    """
    detection: DetectionResult | None = None
    if src_lang is None:
        detection = detector.detect(text) if detector is not None else detect_language(text)
        src_lang = detection.lang

    sentences = split_sentences(text) if text.strip() else []

    analysis: AnalysisResult | None = None
    if analyze_text and src_lang:
        try:
            analysis = analyze(text, src_lang, lexicon=lexicon)
        except FileNotFoundError:
            analysis = None

    translations: list[TranslationResult] = []
    translated_text: str | None = None
    if translate_to and engine is not None and src_lang:
        translations = [engine.translate(s, src_lang, translate_to) for s in sentences]
        translated_text = " ".join(t.text for t in translations)

    return PipelineResult(
        text=text,
        src_lang=src_lang,
        detection=detection,
        sentences=sentences,
        analysis=analysis,
        tgt_lang=translate_to if translations else None,
        translations=translations,
        translated_text=translated_text,
    )
