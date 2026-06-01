"""babelebab — a divide-and-conquer toolkit for multilingual NLP.

Two threads live here:

* :mod:`babelebab.segmentation` — splitting text into sentences, plus the
  acronym/numeric helpers that make that reliable.
* :mod:`babelebab.languages` — language metadata (ISO 639 codes, etc.).

The companion ``analysis/`` tree holds the frequency lists and machine
-translation comparisons the lexicon side is built from.
"""

from __future__ import annotations

from .analyze import analyze
from .detect import detect
from .pipeline import PipelineResult, pipeline
from .segmentation import split_sentences

__version__ = "0.0.1"

__all__ = [
    "pipeline",
    "PipelineResult",
    "detect",
    "analyze",
    "split_sentences",
    "__version__",
]
