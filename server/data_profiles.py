"""Detection and helpers for CAPR dataset profiles."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence, Tuple, List

from syllable_parser import build_syllable_parsed_entries


@dataclass(frozen=True)
class DataProfile:
    """Represents one dataset family and how syllables should be parsed."""

    key: str
    description: str
    allow_syllable_fallback: bool

    def build_syllables_parsed(
        self,
        row: Mapping[str, str],
        ipa_syllables: Sequence[str],
    ) -> List[Tuple[str, str]]:
        return build_syllable_parsed_entries(
            row.get("STRUCTURE", ""),
            row.get("TOKENS", ""),
            row.get("IPA", ""),
            ipa_syllables,
            allow_fallback=self.allow_syllable_fallback,
        )


# Canonical profiles currently supported by the pipeline.
BURMISH_PROFILE = DataProfile(
    key="burmish",
    description="Structured syllable tokens with tone markers",
    allow_syllable_fallback=False,
)
GERMANIC_PROFILE = DataProfile(
    key="germanic",
    description="Segmented IPA without explicit structure tokens",
    allow_syllable_fallback=True,
)

_PROFILE_ORDER = (BURMISH_PROFILE, GERMANIC_PROFILE)


def detect_profile(rows: Iterable[Mapping[str, str]]) -> DataProfile:
    """Infer the dataset profile based on TSV row contents.

    The current heuristics distinguish between datasets that retain explicit
    structure/token annotations (Burmish pipeline) and those that only provide
    plain IPA syllables (Germanic pipeline).
    """

    structured_hits = 0
    unstructured_hits = 0
    inspected = 0

    for inspected, row in enumerate(rows, start=1):
        tokens = (row.get("TOKENS") or "").strip()
        structure = (row.get("STRUCTURE") or "").strip()
        if tokens and " + " in tokens:
            structured_hits += 1
        elif structure and " + " in structure:
            structured_hits += 1
        elif tokens:
            unstructured_hits += 1
        elif structure:
            unstructured_hits += 1
        
        if inspected >= 100:
            break

    if structured_hits:
        return BURMISH_PROFILE
    if unstructured_hits:
        return GERMANIC_PROFILE

    # Fallback: default to Burmish profile so we keep strict checking, the
    # parser will simply return empty syllable slots if nothing is provided.
    return BURMISH_PROFILE


__all__ = [
    "DataProfile",
    "BURMISH_PROFILE",
    "GERMANIC_PROFILE",
    "detect_profile",
]
