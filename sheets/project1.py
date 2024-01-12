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
import decimal
import numpy as np
import enum
from typing import Optional, Tuple, Any
from .utils import *


class Workbook:
    # A workbook containing zero or more named spreadsheets.
    #
    # Any and all operations on a workbook that may affect calculated cell
    # values should cause the workbook's contents to be updated properly.

    def __init__(self):
        """Initialize a new empty workbook."""
        
        # Workbook features
        self.workbook = {}
        self.lower_sheetnames = {}
        self.curr_gen = 1

        # Sheet features
        

    def num_sheets(self) -> int:
        """Returns the number of spreadsheets in the workbook."""

        # Make sure it is always consistent with functions below
        return len(self.workbook.keys())

    def list_sheets(self) -> list[str]:
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

        return list(self.workbook.keys())

    def new_sheet(self, sheet_name: Optional[str] = None) -> tuple[int, str]:
        """Adds a new sheet to the workbook.  If the sheet name is specified, it
        must be unique.  If the sheet name is None, a unique sheet name is
        generated.  "Uniqueness" is determined in a case-insensitive manner,
        but the case specified for the sheet name is preserved.

        The function returns a tuple with two elements:
        (0-based index of sheet in workbook, sheet name).  This allows the
        function to report the sheet's name when it is auto-generated.

        If the spreadsheet name is an empty string (not None), or it is
        otherwise invalid, a ValueError is raised."""

        # TODO: Modify to return an error if whitespaces etc.

        # handles empty string sheet name
        index = 0

        # Input not given
        if not sheet_name:
            sheet_name = "Sheet" + str(self.curr_gen)
            self.curr_gen += 1
            # return sheet_name

        # Input given
        sheet_name = clearWhiteSpaceEdges(sheet_name)
        if sheet_name == "":
            raise ValueError("Sheet name cannot be an empty string")
        elif sheet_name.lower() in self.lower_sheetnames:
            raise ValueError("Sheet name already exists. Select a different name")
        # handles invalid char for name
        else:
            allowed_chars = ".?!,:;!@#$%^&*()-_abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            for char in sheet_name:
                if char not in allowed_chars:
                    raise ValueError(
                        "Sheet name can only have the following characters: .?!,:;!@#$%^&*()-_"
                    )
        # if sheet name doesn't exist, generate name
        self.lower_sheetnames[sheet_name.lower()] = sheet_name

        self.workbook[sheet_name] = Sheet(sheet_name)
        self.lower_sheetnames[sheet_name.lower()] = sheet_name

        return len(self.workbook.keys()) - 1, sheet_name

    def del_sheet(self, sheet_name: str) -> None:
        # Delete the spreadsheet with the specified name.
        #
        # The sheet name match is case-insensitive; the text must match but the
        # case does not have to.
        #
        # If the specified sheet name is not found, a KeyError is raised.
        if sheet_name.lower() in self.lower_sheetnames:
            original_sheetname = self.lower_sheetnames[sheet_name.lower()]
            del self.workbook[original_sheetname]
        else:
            raise KeyError("Sheet not found")

    def get_sheet_extent(self, sheet_name: str) -> tuple[int, int]:
        # Return a tuple (num-cols, num-rows) indicating the current extent of
        # the specified spreadsheet.
        #
        # The sheet name match is case-insensitive; the text must match but the
        # case does not have to.
        #
        # If the specified sheet name is not found, a KeyError is raised.
        if sheet_name not in self.list_sheets():
            raise KeyError("Sheet not found.")

        pass

    def set_cell_contents(
        self, sheet_name: str, location: str, contents: Optional[str]
    ) -> None:
        # Set the contents of the specified cell on the specified sheet.
        #
        # The sheet name match is case-insensitive; the text must match but the
        # case does not have to.  Additionally, the cell location can be
        # specified in any case.
        #
        # If the specified sheet name is not found, a KeyError is raised.
        # If the cell location is invalid, a ValueError is raised.
        #
        # A cell may be set to "empty" by specifying a contents of None.
        #
        # Leading and trailing whitespace are removed from the contents before
        # storing them in the cell.  Storing a zero-length string "" (or a
        # string composed entirely of whitespace) is equivalent to setting the
        # cell contents to None.
        #
        # If the cell contents appear to be a formula, and the formula is
        # invalid for some reason, this method does not raise an exception;
        # rather, the cell's value will be a CellError object indicating the
        # nature of the issue.



        pass

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
        pass

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
        pass


class Sheet:
    def __init__(self, sheet_name):
        self.sheet_name = sheet_name
        self.data = {}
        self.x_extent = []
        self.y_extent = [] 

    # this function updates self.extent_x
    # set increment to true if we are adding a value, and false if we are removing
    def update_extent_x(self, idx : int, increment : bool):
        x_len = len(self.x_extent)
        match increment:
            case True:
                #increment self.extent_x
                # if idx is out of bounds, extend self.extent_x with 0's THEN increment
                if idx >= x_len:
                    for i in range(0, idx + 1):
                        self.x_extent.append(0)
                self.x_extent[idx] += 1
            case False:
                # decrement self.extent_x
                self.x_extent[idx] -= 1

                new_end_idx = x_len
                for i in range(x_len, -1, -1):
                    if self.x_extent[i] == 0:
                        new_end_idx -= 1
                    else:
                        break
                self.x_extent = self.x_extent[:new_end_idx]

    def update_extent_y(self, idx : int, increment : bool):
        y_len = len(self.y_extent)
        match increment:
            case True:
                #increment self.extent_y
                # if idx is out of bounds, extend self.extent_y with 0's THEN increment
                if idx >= y_len:
                    for i in range(0, idx + 1):
                        self.y_extent.append(0)
                self.y_extent[idx] += 1
            case False:
                # decrement self.extent_y
                self.y_extent[idx] -= 1

                new_end_idx = y_len
                for i in range(y_len, -1, -1):
                    if self.y_extent[i] == 0:
                        new_end_idx -= 1
                    else:
                        break
                self.y_extent = self.y_extent[:new_end_idx]

    def getName(self):
        return self.sheet_name

    def set_cell_contents(self, location: str, contents: Optional[str]) -> None:
        return
        # If the cell location is invalid, a ValueError is raised.
        #
        # A cell may be set to "empty" by specifying a contents of None.
        #
        # Leading and trailing whitespace are removed from the contents before
        # storing them in the cell.  Storing a zero-length string "" (or a
        # string composed entirely of whitespace) is equivalent to setting the
        # cell contents to None.
        #
        # If the cell contents appear to be a formula, and the formula is
        # invalid for some reason, this method does not raise an exception;
        # rather, the cell's value will be a CellError object indicating the
        # naure of the issue.

        # TODO: CALL isValidLoc() to check loc is valid
        # if not, raise ValueError()

        # TODO: ELSE
        # USE UTIL TO CONVERT LOC TO (idx-x, idx-y) using locToIdx() from utils

        # TODO: check if self.data needs to be resized (possibly create helper functions resizing)
        # check if idx-x is out of bounds -> resize
        # check if idx-y is out of bounds -> resize
        # could be done with helper by calling resize(idx-x, idx-y)

        # TODO: grab self.data[idx-x][idx-y]
        # CHECK IF CELL IS SET
        # if so, no need to update self.extent_x or self.extent_y
        # otherwise if cell == (None, None), update self.extent_x and/or self.extent_y (possibly create helper functions for each of these)
        # could be done with helper functions update_extent_x(idx-y) and update_extent_y(idx-x)

        # TODO: UPDATE CELL CONTENTS
        # CHECK contents == None
        # REMOVE WHITESPACE
        # CHECK contents == ""
        # CHECK STRING contents[0] == "'"
        # CHECK FORMULA contents[0] == "="
        # CHECK VALID FORMULA, otherwise set VALUE as APPROPRIATE CELL ERROR
        # ELSE NUM

        # TODO: UPDATE CELL VALUE ACCORDINGLY
        # TODO: CHECK DEPENDENCIES TO SEE IF ANY OTHER CELLS
        #       NEED PROPOGATING THE VALUE CHANGE
        
    
        # if contents == "":
        #     return

        # # SET CONTENTS
        # self.contents = cont

        # # SET VALUE
        # if cont[0] == "'":
        #     self.value = cont[1:]
        # elif cont[0] == "=":
        #     self.value = cont
        # else:
        #     try:
        #         self.value = decimal.Decimal(cont)
        #     except:
        #         raise ValueError("This type not supported.")

    def getCell(self, location: str) -> tuple[str, Any]:
        # This is not needed?
        pass 


# class Cell:

#     def __init__(self):
#         self.contents = None
#         self.value = None
    
#     def setContentValue(self, cont : str):
#         if cont == "":
#             return

#         # SET CONTENTS
#         self.contents = cont

#         # SET VALUE
#         if cont[0] == "'":
#             self.value = cont[1:]
#         elif cont[0] == "=":
#             self.value = cont
#         else:
#             try:
#                 self.value = decimal.Decimal(cont)
#             except:
#                 raise ValueError("This type not supported.")

#         return

#     def getContent(self) -> str:
#         return self.contents
    
#     def getValue(self) -> Any:
#         return self.value

