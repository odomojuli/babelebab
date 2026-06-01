"""An offline engine backed by the recorded translations in ``analysis/``.

Each instance replays one provider's output (e.g. ``DEEPL``) from the
``analysis/top1k-translate`` data set, aligning the English source list with a
provider's translations line by line. It needs no network and powers the
``compare`` / ``best_pick`` demos and the test-suite without downloading models.

File lengths vary slightly between providers, so alignment is by index up to
the shorter of the two files; the high-frequency head of the list (where the
tests live) is consistent across providers.
"""
from __future__ import annotations

import os
from pathlib import Path

from ..base import Engine, TranslationResult

_SOURCE_FILE = "eng_lemma_values_top1k.txt"


def _default_data_root() -> Path:
    env = os.environ.get("BABELEBAB_DATA_ROOT")
    if env:
        return Path(env)
    # <repo>/src/babelebab/translate/engines/replay.py -> <repo>/analysis/top1k-translate
    return Path(__file__).resolve().parents[4] / "analysis" / "top1k-translate"


class ReplayEngine(Engine):
    def __init__(
        self,
        provider: str,
        *,
        data_root: str | os.PathLike[str] | None = None,
        name: str | None = None,
    ) -> None:
        self.provider = provider.upper()
        self.name = name or f"replay:{self.provider.lower()}"
        self._data_root = Path(data_root) if data_root is not None else _default_data_root()
        self._cache: dict[tuple[str, str], dict[str, str]] = {}

    def _load(self, src_lang: str, tgt_lang: str) -> dict[str, str]:
        key = (src_lang, tgt_lang)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        src_path = self._data_root / _SOURCE_FILE
        pair_dir = self._data_root / f"{src_lang}-{tgt_lang}-top1k"
        prov_path = pair_dir / f"{tgt_lang}_{self.provider}_top1k.txt"
        if not src_path.exists() or not prov_path.exists():
            raise FileNotFoundError(
                f"{self.name}: missing replay data for {src_lang}->{tgt_lang} "
                f"(looked for {prov_path})"
            )
        sources = src_path.read_text(encoding="utf-8").splitlines()
        targets = prov_path.read_text(encoding="utf-8").splitlines()
        mapping = {
            s.strip().lower(): t.strip()
            for s, t in zip(sources, targets)
            if s.strip() and t.strip()
        }
        self._cache[key] = mapping
        return mapping

    def translate(self, text: str, src_lang: str, tgt_lang: str) -> TranslationResult:
        mapping = self._load(src_lang, tgt_lang)
        recorded = mapping.get(text.strip().lower())
        if recorded is None:
            raise KeyError(
                f"{self.name}: no recorded translation for {text!r} ({src_lang}->{tgt_lang})"
            )
        return TranslationResult(
            text=recorded,
            source=text,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
            engine=self.name,
            meta={"provider": self.provider},
        )
