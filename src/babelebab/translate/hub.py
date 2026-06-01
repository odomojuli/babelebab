"""The public translation hub: translate, compare, and pick across engines."""
from __future__ import annotations

from collections import Counter
from typing import Union

from .base import Engine, TranslationResult
from .registry import available, get

EngineRef = Union[str, Engine]


def _resolve(engine: EngineRef) -> Engine:
    return engine if isinstance(engine, Engine) else get(engine)


def translate(
    text: str, src_lang: str, tgt_lang: str, engine: EngineRef
) -> TranslationResult:
    """Translate ``text`` with a single engine (by name or instance)."""
    return _resolve(engine).translate(text, src_lang, tgt_lang)


def compare(
    text: str,
    src_lang: str,
    tgt_lang: str,
    engines: list[EngineRef] | None = None,
) -> list[TranslationResult]:
    """Translate ``text`` with several engines and collect the results.

    ``engines`` defaults to every registered engine. Engines that cannot
    translate the input (e.g. a replay engine with no record for it) are
    skipped rather than raising.
    """
    refs: list[EngineRef] = list(engines) if engines is not None else list(available())
    results: list[TranslationResult] = []
    for ref in refs:
        try:
            results.append(_resolve(ref).translate(text, src_lang, tgt_lang))
        except Exception:
            continue
    return results


def best_pick(
    text: str,
    src_lang: str,
    tgt_lang: str,
    engines: list[EngineRef] | None = None,
    *,
    strategy: str = "consensus",
) -> TranslationResult | None:
    """Pick a single best translation across engines.

    The only strategy today is ``"consensus"`` -- the translation the most
    engines agree on, ties broken by engine order. Returns ``None`` when no
    engine could translate the input.
    """
    results = compare(text, src_lang, tgt_lang, engines)
    if not results:
        return None
    if strategy != "consensus":
        raise ValueError(f"unknown strategy {strategy!r}")
    counts = Counter(r.text for r in results)
    winner, _ = counts.most_common(1)[0]
    chosen = next(r for r in results if r.text == winner)
    return TranslationResult(
        text=chosen.text,
        source=text,
        src_lang=src_lang,
        tgt_lang=tgt_lang,
        engine="best_pick",
        meta={
            "strategy": "consensus",
            "winning_engine": chosen.engine,
            "votes": dict(counts),
            "n_engines": len(results),
        },
    )
