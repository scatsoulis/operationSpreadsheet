# Generally useful functions for the sheets package
import re


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

def locToIdx(location : str) -> tuple[int, int]:
    # this will only be called with a valid location string

    # convert the location string to (idx, idx)

    # return tuple of x, y indices.

    pass

def isValidLoc(location : str) -> bool:

    # if loc has punctuation -> false

    # if invalid loc -> return false

    # else return true

    pass

if __name__ == "__main__":
    data1 = clearWhiteSpaceEdges("  This is a test  ")
    data2 = clearWhiteSpaceAll("  This is a test  ")

    print(data1)
    print(data2)
