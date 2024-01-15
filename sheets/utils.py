# Generally useful functions for the sheets package
import re
import sys
import decimal
from typing import Optional, Tuple, Any


def testCaseInsensitive(newString: str, stringList: str):
    """Compare a new string to a list of strings, case insensitive"""

    for string in stringList:
        if newString.lower() == string.lower():
            raise ValueError("Name already exists - please choose something else")

    print(f"Sensitivity test passed for {newString}")


def clearWhiteSpaceEdges(data: str):
    """Clears leading and trailing whitespaces of a given input"""

    return data.strip()


def clearWhiteSpaceAll(data: str):
    """Clears all whitespaces from given input"""

    return re.sub(r"\s+", "", data)  # Replaces any whitespace with an empty string


def testEmptyCell():
    pass


def locToIdx(location: str) -> Tuple[int, int]:
    """Convert location string to tuple of indices"""
    # Question: uppercase letters only? OH (recall possible mixing)

    # Check for whitespaces/order/punctuation/repetition
    pattern = r"^[a-zA-Z]+[0-9]+$"
    assert bool(
        re.match(pattern, location)
    ), "Location pattern is wrong (whitespaces/order/punctuation/repetition/missing row,col)"

    # Split string and number
    letters = ""
    numbers = ""
    for char in location:
        if char.isalpha():
            letters += char
        elif char.isdigit():
            numbers += char

    # Size check
    assert len(letters) <= 4 and len(numbers) <= 4, "Max size (ZZZZ9999) exceeded."

    # Convert letter string into idx
    base = ord("A") - 1
    letters = letters.upper()

    return (
        sum(
            26 ** (len(letters) - i - 1) * (ord(char) - base)
            for i, char in enumerate(letters)
        )
        - 1,
        int(numbers) - 1,
    )


def isLocValid(location: str):
    # Pattern check
    pattern = r"^[a-zA-Z]+[0-9]+$"
    if not bool(re.match(pattern, location)):
        raise ValueError(
            "Location pattern is wrong (whitespaces/order/punctuation/repetition/missing row,col)"
        )

    # Split string and number
    letters = ""
    numbers = ""
    for char in location:
        if char.isalpha():
            letters += char
        elif char.isdigit():
            numbers += char

    # Size check
    if len(letters) > 4 or len(numbers) > 4:
        raise ValueError("Max size (ZZZZ9999) exceeded.")


def strip_zeros(decimal_number: decimal.Decimal) -> decimal.Decimal:
    """Strips trailing zeros from a decimal number.

    Args:
        decimal_number: A decimal.Decimal object.

    Returns:
        A decimal.Decimal object with trailing zeros removed.

    Note: recall warning if input is very close to 0
    """

    if isinstance(decimal_number, str):
        raise TypeError("Input must be a decimal.Decimal object, not a string.")

    return decimal_number.quantize(decimal.Decimal("1"))


if __name__ == "__main__":
    sys.exit()
    print(strip_zeros(decimal.Decimal("0.00000")))
    data1 = clearWhiteSpaceEdges("")
    print(type(data1))
    print(locToIdx("a1"))
    print(locToIdx("AB12"))
    print(locToIdx("ZZZZ9999"))

    data2 = clearWhiteSpaceAll("  This is a test  ")

    print(data1)
    print(data2)
