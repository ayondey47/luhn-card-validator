"""Card-number validation core — pure functions, no I/O.

Implements the Luhn (mod-10) checksum used by virtually all payment cards, plus
issuer-brand detection from the well-known prefix/length rules. This is the kind
of cheap, deterministic check a fraud or payments pipeline runs before spending
money on a real authorization round-trip.

Security note: this module only inspects card numbers. It never stores, logs, or
transmits them. Callers handling real PANs should treat them as PCI-scoped data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


def _digits(card_number: str) -> list[int]:
    """Strip spaces/dashes and return the numeric digits as a list of ints."""
    cleaned = re.sub(r"[\s-]", "", card_number)
    if not cleaned.isdigit():
        raise ValueError("card number must contain only digits, spaces, or dashes")
    return [int(c) for c in cleaned]


def luhn_checksum(card_number: str) -> int:
    """Return the Luhn checksum (0 means the number is valid)."""
    digits = _digits(card_number)
    total = 0
    # Double every second digit counting from the right.
    for index, digit in enumerate(reversed(digits)):
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10


def is_luhn_valid(card_number: str) -> bool:
    """True if ``card_number`` passes the Luhn check."""
    try:
        return luhn_checksum(card_number) == 0
    except ValueError:
        return False


# (brand, length set, list of compiled prefix predicates)
def _in_range(value: str, low: int, high: int) -> bool:
    width = len(str(high))
    return low <= int(value[:width]) <= high


def detect_brand(card_number: str) -> str:
    """Identify the card brand from prefix and length rules.

    Returns the brand name, or "Unknown" if no rule matches.
    """
    digits = re.sub(r"[\s-]", "", card_number)
    if not digits.isdigit():
        return "Unknown"
    n = len(digits)

    if digits[0] == "4" and n in (13, 16, 19):
        return "Visa"
    if n == 16 and (_in_range(digits, 51, 55) or _in_range(digits, 2221, 2720)):
        return "Mastercard"
    if n == 15 and digits[:2] in ("34", "37"):
        return "American Express"
    if n == 16 and (
        digits.startswith("6011")
        or digits[:2] == "65"
        or _in_range(digits, 644, 649)
    ):
        return "Discover"
    if n == 14 and (_in_range(digits, 300, 305) or digits[:2] in ("36", "38")):
        return "Diners Club"
    if n == 16 and _in_range(digits, 3528, 3589):
        return "JCB"
    return "Unknown"


@dataclass
class CardInfo:
    """Structured result of inspecting a card number."""

    masked: str
    brand: str
    bin: str
    length: int
    luhn_valid: bool

    def summary(self) -> str:
        status = "valid" if self.luhn_valid else "INVALID (Luhn check failed)"
        return (
            f"Card:  {self.masked}\n"
            f"Brand: {self.brand}\n"
            f"BIN:   {self.bin}\n"
            f"Luhn:  {status}"
        )


def _mask(digits: str) -> str:
    """Mask all but the first 6 (BIN) and last 4 digits."""
    if len(digits) <= 10:
        return "*" * len(digits)
    return f"{digits[:6]}{'*' * (len(digits) - 10)}{digits[-4:]}"


def parse_card(card_number: str) -> CardInfo:
    """Validate and describe a card number without exposing the full PAN."""
    digits = re.sub(r"[\s-]", "", card_number)
    if not digits.isdigit():
        raise ValueError("card number must contain only digits, spaces, or dashes")
    return CardInfo(
        masked=_mask(digits),
        brand=detect_brand(digits),
        bin=digits[:6],
        length=len(digits),
        luhn_valid=is_luhn_valid(digits),
    )
