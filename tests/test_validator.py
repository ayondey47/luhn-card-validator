"""Tests for the Luhn validator and brand detection.

All card numbers below are the standard publicly published *test* numbers used
by payment processors. They pass the Luhn check but are not real accounts.
"""

import pytest

from cardcheck import (
    detect_brand,
    is_luhn_valid,
    luhn_checksum,
    parse_card,
)

# Well-known processor test numbers.
VISA = "4111111111111111"
VISA_13 = "4222222222222"
MASTERCARD = "5555555555554444"
MASTERCARD_2 = "2223003122003222"
AMEX = "378282246310005"
DISCOVER = "6011111111111117"
DINERS = "30569309025904"
JCB = "3530111333300000"


def test_luhn_valid_known_numbers():
    for number in (VISA, MASTERCARD, AMEX, DISCOVER, DINERS, JCB):
        assert is_luhn_valid(number), number


def test_luhn_checksum_zero_when_valid():
    assert luhn_checksum(VISA) == 0


def test_luhn_rejects_transposed_digit():
    # Flip the last digit -> should fail.
    assert not is_luhn_valid("4111111111111112")


def test_luhn_handles_spaces_and_dashes():
    assert is_luhn_valid("4111 1111 1111 1111")
    assert is_luhn_valid("4111-1111-1111-1111")


def test_non_numeric_is_invalid_not_crash():
    assert is_luhn_valid("not-a-card") is False


@pytest.mark.parametrize(
    "number,brand",
    [
        (VISA, "Visa"),
        (VISA_13, "Visa"),
        (MASTERCARD, "Mastercard"),
        (MASTERCARD_2, "Mastercard"),
        (AMEX, "American Express"),
        (DISCOVER, "Discover"),
        (DINERS, "Diners Club"),
        (JCB, "JCB"),
        ("9999999999999999", "Unknown"),
    ],
)
def test_brand_detection(number, brand):
    assert detect_brand(number) == brand


def test_parse_card_masks_pan():
    info = parse_card(VISA)
    assert info.brand == "Visa"
    assert info.bin == "411111"
    assert info.luhn_valid
    # Middle digits hidden; first 6 and last 4 visible.
    assert info.masked.startswith("411111")
    assert info.masked.endswith("1111")
    assert "*" in info.masked


def test_parse_card_rejects_garbage():
    with pytest.raises(ValueError):
        parse_card("abcd")


def test_amex_summary_reports_brand():
    text = parse_card(AMEX).summary()
    assert "American Express" in text
    assert "valid" in text
