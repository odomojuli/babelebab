"""A local, offline translation engine built on CTranslate2 + SentencePiece.

This is the production-grade local path: CPU inference with int8 quantization
and no torch/CUDA at run time. It needs the optional ``local`` extra::

    pip install "babelebab[local]"

plus a model directory converted with ``ct2-transformers-converter`` (e.g. an
OPUS-MT pair), which also provides the SentencePiece model(s). The heavy
imports are deferred until first use, so importing babelebab never requires
them.
"""
from __future__ import annotations

import os
from typing import Any

from ..base import Engine, TranslationResult


class CTranslate2Engine(Engine):
    def __init__(
        self,
        model_dir: str | os.PathLike[str],
        *,
        sp_source: str | os.PathLike[str],
        sp_target: str | os.PathLike[str] | None = None,
        device: str = "cpu",
        compute_type: str = "int8",
        name: str = "ctranslate2",
    ) -> None:
        self.name = name
        self._model_dir = os.fspath(model_dir)
        self._sp_source = os.fspath(sp_source)
        self._sp_target = os.fspath(sp_target) if sp_target is not None else self._sp_source
        self._device = device
        self._compute_type = compute_type
        self._translator: Any = None
        self._sp_src: Any = None
        self._sp_tgt: Any = None

    def _ensure_loaded(self) -> None:
        if self._translator is not None:
            return
        try:
            import ctranslate2
            import sentencepiece as spm
        except ImportError as exc:  # pragma: no cover - only without the extra
            raise ImportError(
                'CTranslate2Engine requires the "local" extra: '
                'pip install "babelebab[local]"'
            ) from exc
        self._translator = ctranslate2.Translator(
            self._model_dir, device=self._device, compute_type=self._compute_type
        )
        self._sp_src = spm.SentencePieceProcessor(model_file=self._sp_source)
        self._sp_tgt = spm.SentencePieceProcessor(model_file=self._sp_target)

    def translate(self, text: str, src_lang: str, tgt_lang: str) -> TranslationResult:
        self._ensure_loaded()
        tokens = self._sp_src.encode(text, out_type=str)
        output = self._translator.translate_batch([tokens])
        translated = self._sp_tgt.decode(output[0].hypotheses[0])
        return TranslationResult(
            text=translated,
            source=text,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
            engine=self.name,
            meta={"model_dir": self._model_dir, "device": self._device},
        )
