"""What each recording's licence lets us do, and what a finished mix owes its sources.

Cutting words out of a song and rearranging them makes an *adaptation*, so:
- No-Derivatives (ND) licences are never usable.
- Non-Commercial (NC) licences are only usable in personal mode (``--allow-nc``), never in paid renders.
- Share-Alike (SA) licences are usable, but the output must be shared under the same terms.
- Anything we can't recognise is refused.

Licences are stored in the manifest as a Creative Commons URL ("https://creativecommons.org/licenses/by/4.0/"),
an SPDX-style code ("CC-BY-4.0", "CC0-1.0"), or one of our own codes for audio that isn't CC:
"OWNED" (we made or commissioned it), "ROYALTY-FREE" (bought; terms checked by hand) or "PD" (public domain).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_CC_URL = re.compile(r"creativecommons\.org/(?:licenses|publicdomain)/([a-z+\-]+)/(\d\.\d)", re.I)
_CC_CODE = re.compile(r"^CC[- ]?(0|BY(?:-NC)?(?:-SA|-ND)?)[- ]?(\d\.\d)?$", re.I)
_NAMES = {  # free-text names some catalogues use (Freesound's older API, ccMixter's licence_name)
    "creative commons 0": "CC0-1.0",
    "attribution": "CC-BY-4.0",
    "attribution noncommercial": "CC-BY-NC-4.0",
}


@dataclass(frozen=True)
class License:
    code: str  # e.g. "CC-BY-SA-3.0", "CC0-1.0", "OWNED"
    url: str = ""
    attribution: bool = False
    share_alike: bool = False
    noncommercial: bool = False
    no_derivatives: bool = False

    @property
    def label(self) -> str:
        if self.code.startswith("CC-"):
            return "CC " + self.code[3:].rsplit("-", 1)[0] + " " + self.code.rsplit("-", 1)[1]
        return {"CC0-1.0": "CC0 1.0", "PD": "Public domain", "OWNED": "Owned", "ROYALTY-FREE": "Royalty-free"}.get(
            self.code, self.code
        )


def _cc(kind: str, version: str) -> License:
    kind = kind.lower()
    if kind in ("zero", "0"):
        return License("CC0-1.0", "https://creativecommons.org/publicdomain/zero/1.0/")
    if kind == "mark":
        return License("PD", "https://creativecommons.org/publicdomain/mark/1.0/")
    if kind in ("sampling+", "sampling", "nc-sampling+"):
        # Sampling licences allow transforming samples (our use); NC sampling+ forbids commercial use.
        return License(
            f"CC-{kind.upper()}-{version}",
            f"https://creativecommons.org/licenses/{kind}/{version}/",
            attribution=True,
            noncommercial=kind.startswith("nc"),
        )
    parts = kind.split("-")
    if parts[0] != "by":
        raise ValueError(kind)
    return License(
        f"CC-{kind.upper()}-{version}",
        f"https://creativecommons.org/licenses/{kind}/{version}/",
        attribution=True,
        share_alike="sa" in parts,
        noncommercial="nc" in parts,
        no_derivatives="nd" in parts,
    )


def parse_license(text: str) -> License | None:
    """Recognise a licence from a URL, code or catalogue name. None if unknown."""
    text = (text or "").strip()
    if not text:
        return None
    upper = text.upper()
    if upper in ("OWNED", "ROYALTY-FREE", "PD"):
        return License(upper)
    if text.lower() in _NAMES:
        return parse_license(_NAMES[text.lower()])
    if m := _CC_URL.search(text):
        try:
            return _cc(m.group(1), m.group(2))
        except ValueError:
            return None
    if m := _CC_CODE.match(text):
        kind = "zero" if m.group(1) == "0" else m.group(1)
        return _cc(kind, m.group(2) or ("1.0" if kind == "zero" else "4.0"))
    return None


@dataclass(frozen=True)
class LicensePolicy:
    allow_noncommercial: bool = False  # personal mode only; never for paid renders

    def why_not(self, lic: License | None) -> str | None:
        """None if usable, otherwise the reason it isn't."""
        if lic is None:
            return "licence not recognised"
        if lic.no_derivatives:
            return f"{lic.label} forbids remixing"
        if lic.noncommercial and not self.allow_noncommercial:
            return f"{lic.label} is non-commercial (use --allow-nc for personal use)"
        return None

    def allows(self, lic: License | None) -> bool:
        return self.why_not(lic) is None


@dataclass
class OutputTerms:
    """What anyone sharing the finished audio must do."""

    attribution: bool
    noncommercial: bool
    share_alike: str | None  # licence the output must be shared under, if any
    conflict: bool  # mixes Share-Alike licences that can't be combined

    @property
    def notice(self) -> str:
        if self.conflict:
            return (
                "Warning: this mix combines CC BY-SA and CC BY-NC-SA recordings, which can't legally be combined. "
                "Shuffle or turn off non-commercial songs."
            )
        if self.share_alike:
            use = "non-commercially " if self.noncommercial else ""
            return f"You may share this {use}under {self.share_alike}, with the credits below."
        if self.noncommercial:
            return "Personal / non-commercial use only. Keep the credits below with it."
        if self.attribution:
            return "Free to share and use, including commercially, as long as the credits below go with it."
        return "No attribution required (credits shown for fun)."


def output_terms(licenses: list[License]) -> OutputTerms:
    sa = [lic for lic in licenses if lic.share_alike]
    nc = any(lic.noncommercial for lic in licenses)
    conflict = any(lic.noncommercial for lic in sa) and any(not lic.noncommercial for lic in sa)
    share_alike = None
    if sa:
        # BY-SA 3.0 adaptations may be released under a later version, so 4.0 covers a mix of both.
        share_alike = "CC BY-NC-SA 4.0" if nc else "CC BY-SA 4.0"
    return OutputTerms(
        attribution=any(lic.attribution for lic in licenses),
        noncommercial=nc,
        share_alike=share_alike,
        conflict=conflict,
    )
