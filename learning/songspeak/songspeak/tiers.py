"""What each plan is allowed to do."""

from __future__ import annotations

from dataclasses import dataclass

MIX_VARIETY = "variety"  # as many different songs as possible ("ransom note")
MIX_FEWEST_SONGS = "fewest-songs"  # stick to a few songs so it sounds more coherent


@dataclass(frozen=True)
class Tier:
    name: str
    max_chars: int
    moods: bool
    mix_modes: tuple[str, ...]


FREE = Tier("free", max_chars=300, moods=False, mix_modes=(MIX_VARIETY,))
PREMIUM = Tier("premium", max_chars=30_000, moods=True, mix_modes=(MIX_VARIETY, MIX_FEWEST_SONGS))

TIERS = {t.name: t for t in (FREE, PREMIUM)}


class TierError(PermissionError):
    """The request uses something the user's plan does not include."""


def check_request(tier: Tier, mood: str | None, mix: str) -> None:
    if mood and not tier.moods:
        raise TierError("Mood selection is a premium feature.")
    if mix not in tier.mix_modes:
        raise TierError(f"Mix mode {mix!r} is not on the {tier.name} plan (available: {', '.join(tier.mix_modes)}).")
