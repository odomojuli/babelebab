"""Canonical sentence splitter.

``split_sentences`` is the single public entry point for turning a chunk of
text into a list of sentences. Everything downstream (the test-suite, future
tooling) imports from here, so the underlying algorithm can be swapped out — a
stricter rules engine, a statistical model, a per-language strategy — without
touching callers.

Today it delegates to the regex prototype in
:mod:`babelebab.segmentation.naive_regex`. That is a deliberate *baseline*, not
the finished article: the golden-rule suites under ``golden_rules/`` describe
the behaviour we are aiming for across languages.
"""
from __future__ import annotations

from .naive_regex import split_into_sentences


def split_sentences(text: str) -> list[str]:
    """Split ``text`` into a list of sentence strings.

    Args:
        text: Input text, possibly containing many sentences.

    Returns:
        A list of sentences with surrounding whitespace stripped.
    """
    return split_into_sentences(text)
