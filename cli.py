"""Command-line interface for the Luhn card validator.

Usage:
    python cli.py 4111111111111111
    python cli.py "4111 1111 1111 1111" "378282246310005"
"""

from __future__ import annotations

import argparse
import sys

from cardcheck import parse_card


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate payment-card numbers (Luhn) and detect the brand."
    )
    parser.add_argument("numbers", nargs="+", help="One or more card numbers")
    args = parser.parse_args(argv)

    any_invalid = False
    for i, number in enumerate(args.numbers):
        if i:
            print("-" * 32)
        try:
            info = parse_card(number)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            any_invalid = True
            continue
        print(info.summary())
        if not info.luhn_valid:
            any_invalid = True

    return 1 if any_invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
