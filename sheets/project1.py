# ==============================================================================
# Caltech CS130 - Winter 2023
#
# This file specifies the API that we expect your implementation to conform to.
# You will likely want to move these classes into various files, but the tests
# will expect these to be available when the "sheets" module is imported.

# If you are unfamiliar with Python 3 type annotations, see the Python standard
# library documentation for the typing module here:
#
#     https://docs.python.org/3/library/typing.html
#
# NOTE:  THIS FILE WILL NOT WORK AS-IS.  You are expected to incorporate it
#        into your project in whatever way you see fit.
import sys
import scipy
import decimal
import numpy as np
import enum
from typing import Optional, Tuple, Any, List
from utils import isLocValid, locToIdx, clearWhiteSpaceEdges


class Workbook:
    # A workbook containing zero or more named spreadsheets.
    #
    # Any and all operations on a workbook that may affect calculated cell
    # values should cause the workbook's contents to be updated properly.

    def __init__(self):
        """Initialize a new empty workbook."""

        # Workbook features
        # TODO: make sure initializations preserve correct format as flowchat
        
        # maps lowercase sheetname to data dict 
        self.data = {}

        # maps lowercase sheetname to original name
        self.lower_sheetnames = {}

        # maps lowercase sheetname to extents
        self.extents = {}

        self.curr_gen = 1
        self.formula_graph = None # Graph object


    def num_sheets(self) -> int:
        """Returns the number of spreadsheets in the workbook."""
        
        return len(self.data.keys())

    def list_sheets(self) -> List[str]:
        """Return a list of the spreadsheet names in the workbook, with the
        capitalization specified at creation, and in the order that the sheets
        appear within the workbook.

        In this project, the sheet names appear in the order that the user
        created them; later, when the user is able to move and copy sheets,
        the ordering of the sheets in this function's result will also reflect
        such operations.

        A user should be able to mutate the return-value without affecting the
        workbook's internal state."""
        # Testing note: play around with order ^  - try to break it

        return list(self.lower_sheetnames.values())

    def new_sheet(self, sheet_name: Optional[str] = None) -> Tuple[int, str]:
        """Adds a new sheet to the workbook.  If the sheet name is specified, it
        must be unique.  If the sheet name is None, a unique sheet name is
        generated.  "Uniqueness" is determined in a case-insensitive manner,
        but the case specified for the sheet name is preserved.

        The function returns a tuple with two elements:
        (0-based index of sheet in workbook, sheet name).  This allows the
        function to report the sheet's name when it is auto-generated.

        If the spreadsheet name is an empty string (not None), or it is
        otherwise invalid, a ValueError is raised."""

        # None case
        if not sheet_name:
            sheet_name = "Sheet" + str(self.curr_gen)
            # this catches the case where the auto-generated sheet name is already used
            while sheet_name.lower() in self.lower_sheetnames:
                self.curr_gen += 1
                sheet_name = "Sheet" + str(self.curr_gen)
            self.curr_gen += 1
        else:
            # Error catching
            if sheet_name == "":  # Empty string
                raise ValueError("Sheet name cannot be an empty string.")
            if bool(
                sheet_name.lstrip() != sheet_name or sheet_name.rstrip() != sheet_name
            ):  # Leading/trailing whitespaces
                raise ValueError(
                    "Sheet name cannot contain leading/trailing whitespaces."
                )
            if sheet_name.lower() in self.lower_sheetnames:  # Case-insensitivity
                raise ValueError("Sheet name already exists - select a different one.")
            allowed_chars = " .?!,:;!@#$%^&*()-_abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if any(char not in allowed_chars for char in sheet_name):  # Character check
                raise ValueError("Name contains disallowed characters.")
            # Think about ways to break the above ^

        # Append sheetname to list of existing sheets.
        lower_name = sheet_name.lower()
        self.lower_sheetnames[lower_name] = sheet_name
        self.data[lower_name] = {}
        self.extents[lower_name] = ([0], [0])

        return len(self.lower_sheetnames) - 1, sheet_name

    def del_sheet(self, sheet_name: str) -> None:
        """Delete the spreadsheet with the specified name.

        The sheet name match is case-insensitive; the text must match but the
        case does not have to.

        If the specified sheet name is not found, a KeyError is raised."""

        lower_name = sheet_name.lower()
        if lower_name in self.lower_sheetnames:
            del self.data[lower_name]
            del self.lower_sheetnames[sheet_name.lower()]
            del self.extents[sheet_name.lower()]

            # TODO:
            # REMOVE THE NODES FROM SELF.GRAPH WHICH COME FROM THIS SHEET
            # CHECK IF THIS CAUSES ERRORS IN OTHER SHEETS
            # PROPOGATE ERRORS IF NECESSARY
        
        else:
            raise KeyError("Sheet not found")

    def get_sheet_extent(self, sheet_name: str) -> Tuple[int, int]:
        """Return a tuple (num-cols, num-rows) indicating the current extent of
        the specified spreadsheet.

        The sheet name match is case-insensitive; the text must match but the
        case does not have to.

        If the specified sheet name is not found, a KeyError is raised."""

        lower_name = sheet_name.lower()

        if lower_name not in self.lower_sheetnames:
            raise KeyError("Sheet not found.")

        x_extents = self.extents[lower_name][0]
        y_extents = self.extents[lower_name][1]

        return len(x_extents) - 1, len(y_extents) - 1

    def set_cell_contents(
        self, sheet_name: str, location: str, contents: Optional[str]
    ) -> None:
        """Set the contents of the specified cell on the specified sheet.

        The sheet name match is case-insensitive; the text must match but the
        case does not have to.  Additionally, the cell location can be
        specified in any case.

        If the specified sheet name is not found, a KeyError is raised.
        If the cell location is invalid, a ValueError is raised.

        A cell may be set to "empty" by specifying a contents of None.

        Leading and trailing whitespace are removed from the contents before
        storing them in the cell.  Storing a zero-length string "" (or a
        string composed entirely of whitespace) is equivalent to setting the
        cell contents to None.

        If the cell contents appear to be a formula, and the formula is
        invalid for some reason, this method does not raise an exception;
        rather, the cell's value will be a CellError object indicating the
        nature of the issue."""
        # Cell location checks
        # Sheet name existence

        lower_name = sheet_name.lower()

        if lower_name not in self.lower_sheetnames:
            raise KeyError("Sheet not found.")

        # Cell location check
        isLocValid(location)
        # Get cell location
        x_idx, y_idx = locToIdx(location)

        # Clear leading or trailing whitespace (empty string -> still empty string)
        contents = clearWhiteSpaceEdges(contents)

        # MUST CHECK CONTENTS AND ASSIGN DATA VALUES IN EACH CASE
        if contents == "":  # Empty string
            self.data[lower_name][(x_idx,y_idx)] = (None, None) #TODO: THIS IS NOT INITIALIZING DATA DICTIONARY CORRECTLY
        elif contents[0] == "'":
            self.data[lower_name][(x_idx,y_idx)] = (contents, contents[1:])
        elif contents[0] == "=":  # Formula

            # TODO: 

            # PARSE GRAPH, SEE WHERE INDEX WOULD FIT IN THE CURRENT CONNECTIONS

            # TOPOLOGICAL SORT OF GRAPH

            # FOLLOW SORT ORDER TO EVALULATE FUNCTIONS SUCH THAT ALL PROPPER CELLS GET FILLED IN

            # CHECK VALID FORMULA, otherwise set VALUE as APPROPRIATE CELL ERROR

            pass
            
        else:  # Literal value???
            pass

        # TODO: UPDATE SHEET EXTENT LISTS
        # grab self.data[idx-x][idx-y]
        # CHECK IF CELL IS SET
        # if so, no need to update self.extent_x or self.extent_y
        # otherwise if cell == (None, None), update self.extent_x and/or self.extent_y (possibly create helper functions for each of these)
        # could be done with helper functions update_extent_x(idx-y) and update_extent_y(idx-x)

        # sys.exit()

    def get_cell_contents(self, sheet_name: str, location: str) -> Optional[str]:
        # Return the contents of the specified cell on the specified sheet.
        #
        # The sheet name match is case-insensitive; the text must match but the
        # case does not have to.  Additionally, the cell location can be
        # specified in any case.
        #
        # If the specified sheet name is not found, a KeyError is raised.
        # If the cell location is invalid, a ValueError is raised.
        #
        # Any string returned by this function will not have leading or trailing
        # whitespace, as this whitespace will have been stripped off by the
        # set_cell_contents() function.
        #
        # This method will never return a zero-length string; instead, empty
        # cells are indicated by a value of None.

        lower_name = sheet_name.lower()

        if lower_name not in self.lower_sheetnames:
            raise KeyError("Sheet not found.")

        # cell location check
        isLocValid(location)

        # get cell location
        x_idx, y_idx = locToIdx(location)

        if (x_idx,y_idx) not in self.data[lower_name]:
            return None
        
        content, value = self.data[lower_name][(x_idx,y_idx)]

        if content == "":
            return None
        
        return content

    def get_cell_value(self, sheet_name: str, location: str) -> Any:
        # Return the evaluated value of the specified cell on the specified
        # sheet.
        #
        # The sheet name match is case-insensitive; the text must match but the
        # case does not have to.  Additionally, the cell location can be
        # specified in any case.
        #
        # If the specified sheet name is not found, a KeyError is raised.
        # If the cell location is invalid, a ValueError is raised.
        #
        # The value of empty cells is None.  Non-empty cells may contain a
        # value of str, decimal.Decimal, or CellError.
        #
        # Decimal values will not have trailing zeros to the right of any
        # decimal place, and will not include a decimal place if the value is a
        # whole number.  For example, this function would not return
        # Decimal('1.000'); rather it would return Decimal('1').

        lower_name = sheet_name.lower()

        if lower_name not in self.lower_sheetnames:
            raise KeyError("Sheet not found.")

        # cell location check
        isLocValid(location)

        # get cell location
        x_idx, y_idx = locToIdx(location)

        if (x_idx,y_idx) not in self.data[lower_name]:
            return None
        
        content, value = self.data[lower_name][(x_idx,y_idx)]

        if value == "":
            return None
        
        # TODO: ROUND/FORMAT DECIMALS

        return value


class CellErrorType(enum.Enum):
    """
    This enum specifies the kinds of errors that spreadsheet cells can hold.
    """

    # A formula doesn't parse successfully ("#ERROR!")
    PARSE_ERROR = 1

    # A cell is part of a circular reference ("#CIRCREF!")
    CIRCULAR_REFERENCE = 2

    # A cell-reference is invalid in some way ("#REF!")
    BAD_REFERENCE = 3

    # Unrecognized function name ("#NAME?")
    BAD_NAME = 4

    # A value of the wrong type was encountered during evaluation ("#VALUE!")
    TYPE_ERROR = 5

    # A divide-by-zero was encountered during evaluation ("#DIV/0!")
    DIVIDE_BY_ZERO = 6


class CellError:
    """
    This class represents an error value from user input, cell parsing, or
    evaluation.
    """

    def __init__(
        self,
        error_type: CellErrorType,
        detail: str,
        exception: Optional[Exception] = None,
    ):
        self._error_type = error_type
        self._detail = detail
        self._exception = exception

    def get_type(self) -> CellErrorType:
        """The category of the cell error."""
        return self._error_type

    def get_detail(self) -> str:
        """More detail about the cell error."""
        return self._detail

    def get_exception(self) -> Optional[Exception]:
        """
        If the cell error was generated from a raised exception, this is the
        exception that was raised.  Otherwise this will be None.
        """
        return self._exception

    def __str__(self) -> str:
        return f'ERROR[{self._error_type}, "{self._detail}"]'

    def __repr__(self) -> str:
        return self.__str__()
        pass


class Sheet:
    def __init__(self, sheet_name):
        self.sheet_name = sheet_name
        self.data = {}
        self.x_extent = []
        self.y_extent = []

    # this function updates self.extent_x
    # set increment to true if we are adding a value, and false if we are removing
    def update_extent_x(self, idx: int, increment: bool):
        x_len = len(self.x_extent)
        pass
        # match increment:
        #     case True:
        #         # increment self.extent_x
        #         # if idx is out of bounds, extend self.extent_x with 0's THEN increment
        #         if idx >= x_len:
        #             for i in range(0, idx + 1):
        #                 self.x_extent.append(0)
        #         self.x_extent[idx] += 1
        #     case False:
        #         # decrement self.extent_x
        #         self.x_extent[idx] -= 1

        #         new_end_idx = x_len
        #         for i in range(x_len, -1, -1):
        #             if self.x_extent[i] == 0:
        #                 new_end_idx -= 1
        #             else:
        #                 break
        #         self.x_extent = self.x_extent[:new_end_idx]

    def update_extent_y(self, idx: int, increment: bool):
        y_len = len(self.y_extent)
        pass
        # match increment:
        #     case True:
        #         # increment self.extent_y
        #         # if idx is out of bounds, extend self.extent_y with 0's THEN increment
        #         if idx >= y_len:
        #             for i in range(0, idx + 1):
        #                 self.y_extent.append(0)
        #         self.y_extent[idx] += 1
        #     case False:
        #         # decrement self.extent_y
        #         self.y_extent[idx] -= 1

        #         new_end_idx = y_len
        #         for i in range(y_len, -1, -1):
        #             if self.y_extent[i] == 0:
        #                 new_end_idx -= 1
        #             else:
        #                 break
        #         self.y_extent = self.y_extent[:new_end_idx]

if __name__ == "__main__":
    wb = Workbook()

    print(wb.new_sheet())
    print(wb.new_sheet("The Jimmy"))
    print(wb.new_sheet("Sheet2"))
    print(wb.new_sheet())
    wb.set_cell_contents("The Jimmy", "a1", "'HEY")
    print(wb.get_cell_contents("The Jimmy", "a1"))
    print(wb.get_cell_value("The Jimmy", "a3"))
    print(wb.get_sheet_extent("The Jimmy"))
    print(locToIdx("WWW718"))
    sys.exit()