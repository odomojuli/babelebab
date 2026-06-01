"""A no-op engine that returns the source text unchanged (useful for tests)."""
from __future__ import annotations

from ..base import Engine, TranslationResult


class IdentityEngine(Engine):
    name = "identity"

    def translate(self, text: str, src_lang: str, tgt_lang: str) -> TranslationResult:
        return TranslationResult(
            text=text,
            source=text,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
            engine=self.name,
        )
