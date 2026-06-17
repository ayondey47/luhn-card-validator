# Luhn Card Validator

[![tests](https://github.com/ayondey47/luhn-card-validator/actions/workflows/tests.yml/badge.svg)](https://github.com/ayondey47/luhn-card-validator/actions/workflows/tests.yml)

A dependency-free utility that validates payment-card numbers with the **Luhn
(mod-10) checksum**, detects the issuing **brand** from prefix/length rules, and
extracts the **BIN** — the cheap, deterministic first check a payments or fraud
pipeline runs before paying for a real authorization round-trip.

## What it does

- **Luhn validation** — catches the single-digit typos and transpositions the
  checksum is designed to detect.
- **Brand detection** — Visa, Mastercard (incl. the 2-series range), American
  Express, Discover, Diners Club, and JCB.
- **Safe parsing** — returns a masked PAN (first 6 + last 4) and the BIN. The
  library never stores, logs, or transmits full card numbers.

## Install

Python 3.10+ standard library only.

```bash
git clone https://github.com/ayondey47/luhn-card-validator.git
cd luhn-card-validator
```

## Usage

```bash
python cli.py 4111111111111111
python cli.py "4111 1111 1111 1111" "378282246310005"
```

```
$ python cli.py "4111 1111 1111 1111"
Card:  411111******1111
Brand: Visa
BIN:   411111
Luhn:  valid
```

Exit code is `0` when every number is valid, `1` if any fail — handy in scripts.

## Library use

```python
from cardcheck import is_luhn_valid, detect_brand, parse_card

is_luhn_valid("4111 1111 1111 1111")   # True
detect_brand("378282246310005")        # "American Express"

info = parse_card("4111111111111111")
info.masked        # "411111******1111"
info.brand         # "Visa"
info.luhn_valid    # True
```

## A note on the test numbers

The numbers in `tests/` are the standard publicly published **processor test
numbers** (e.g. Visa `4111 1111 1111 1111`). They satisfy the Luhn check but are
not real accounts.

## Tests

```bash
python -m pytest
```

17 tests cover Luhn validity, transposition detection, separator handling,
brand rules for every supported issuer, and PAN masking.

## License

MIT — see [LICENSE](LICENSE).
