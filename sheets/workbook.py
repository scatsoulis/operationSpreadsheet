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
import lark
import decimal
import numpy as np

from typing import Optional, Tuple, Any
from .formula import FormulaEvaluator, CellRefFinder, CellDependencyGraph
from .utils import isLocValid, locToIdx, clearWhiteSpaceEdges, strip_zeros


class Workbook:
    """A workbook containing zero or more named spreadsheets.

    Any and all operations on a workbook that may affect calculated cell
    values should cause the workbook's contents to be updated properly."""

    def __init__(self):
        """Initialize a new empty workbook."""

        # {lower_name: original_name}
        self.lower_sheetnames = {}

        # {lower_name: {location_str: (contents, value)}}
            # location example: "A9" or "a4"
        self.data = {}

        # {lower_name: ([x_extents], [y_extents])}
        self.extents = {}
        
        # Graph Object
        self.formula_graph = CellDependencyGraph()
        self.curr_gen = 1


    def num_sheets(self) -> int:
        """Returns the number of spreadsheets in the workbook."""
        
        return len(self.data.keys())

    def list_sheets(self) -> Optional[str]:
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
        self.lower_sheetnames[sheet_name.lower()] = sheet_name
        self.data[sheet_name.lower()] = {}
        self.extents[sheet_name.lower()] = ([], [])

        return len(self.lower_sheetnames) - 1, sheet_name

    def del_sheet(self, sheet_name: str) -> None:
        """Delete the spreadsheet with the specified name.

        The sheet name match is case-insensitive; the text must match but the
        case does not have to.

        If the specified sheet name is not found, a KeyError is raised."""

        if sheet_name.lower() in self.lower_sheetnames:
            del self.data[sheet_name.lower()]
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

        x_extents, y_extents = self.extents[lower_name]

        return len(x_extents), len(y_extents)

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
        location = location.lower()

        if lower_name not in self.lower_sheetnames:
            raise KeyError("Sheet not found.")

        # Cell location check and retrieval
        isLocValid(location)
        x_idx, y_idx = locToIdx(location)

        # Clear leading or trailing whitespace (empty string -> still empty string)
        contents = clearWhiteSpaceEdges(contents)

        if location in lower_name:
            curr_contents, curr_value = self.data[lower_name][location]
        else:
            if contents != "":
                self.__update_extents(x_idx, y_idx, lower_name, True)

        # Contents check
        if contents == "":  # Empty string
            if location in self.data[lower_name]:
                del self.data[lower_name][location]
                self.__update_extents(x_idx, y_idx, lower_name, False)
        elif contents[0] == "'":  # String (it's a number, account for possibly leading 0s)
            self.data[lower_name][location] = (contents, contents[1:])
        elif contents[0] == "=":  # Formula parser (first stage)
            print("formula --------")
            # Careful: = follows by another = etc. check for validity of formula body!
            # Also: decimal.Decimal: do not convert NaN nor Infinity etc. they stay as string (only numeric values go through Decimal)
            print(contents)

            # Set up grammar
            parser = lark.Lark.open("formulas.lark", rel_to=__file__, start="formula")
            evaluator = FormulaEvaluator()

            tree = parser.parse(contents)
            print(tree.pretty())

            v = CellRefFinder()
            v.visit(tree)
            print(v.cell_refs)

            for cell_id in v.cell_refs:  # First check validity of all cell IDs
                isLocValid(cell_id)

            for cell_id in v.cell_refs:  # Compute
                print(cell_id)
                # tree.children[0] = 
                value = evaluator.visit(tree)
            # self.data[lower_name][location] = (contents[1:], strip_zeros(value))

            value = evaluator.visit(tree)
            print(f"value = {value} (type is {type(value)})")
            print(self.data)

            # Set contents and value (confirm format of contents)
            self.data[lower_name][location] = (
                contents[1:],
                strip_zeros(value),
            )
            print(self.data[lower_name][(x_idx, y_idx)])

            # Using visitor to scan tree
            # Using transformer to evaluate tree

        # TODO:
        # PARSE GRAPH, SEE WHERE INDEX WOULD FIT IN THE CURRENT CONNECTIONS
        # TOPOLOGICAL SORT OF GRAPH
        # FOLLOW SORT ORDER TO EVALULATE FUNCTIONS SUCH THAT ALL PROPPER CELLS GET FILLED IN
        # CHECK VALID FORMULA, otherwise set VALUE as APPROPRIATE CELL ERROR
        # Think about case 5 + a1


        else:  # Literal value
            self.data[lower_name][location] = (
                contents,
                strip_zeros(decimal.Decimal(contents)),
            )

        print("Literal value:")
        print(type(contents))
        print(self.data)

        # Get cell location

        # Assign content to cell
        # np.reshape(self.data[sheet_name], tuple(np.array(cell_loc) + 1), 2)
        # print(self.data[sheet_name].shape)
        # self.data[sheet_name][cell_loc[1]][cell_loc[0]] = contents

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
        location = location.lower()

        if lower_name not in self.lower_sheetnames:
            raise KeyError("Sheet not found.")

        # cell location check
        isLocValid(location)

        if location not in self.data[lower_name]:
            return None

        content, value = self.data[lower_name][location]

        if content == "":
            return None

        return content

    def get_cell_value(self, sheet_name: str, location: str) -> Any:
        """Return the evaluated value of the specified cell on the specified
        sheet.

        The sheet name match is case-insensitive; the text must match but the
        case does not have to.  Additionally, the cell location can be
        specified in any case.

        If the specified sheet name is not found, a KeyError is raised.
        If the cell location is invalid, a ValueError is raised.

        The value of empty cells is None.  Non-empty cells may contain a
        value of str, decimal.Decimal, or CellError.

        Decimal values will not have trailing zeros to the right of any
        decimal place, and will not include a decimal place if the value is a
        whole number.  For example, this function would not return
        Decimal('1.000'); rather it would return Decimal('1')."""

        lower_name = sheet_name.lower()
        location = location.lower()

        if lower_name not in self.lower_sheetnames:
            raise KeyError("Sheet not found.")

        # cell location check
        isLocValid(location)

        if location not in self.data[lower_name]:
            return None

        content, value = self.data[lower_name][location]

        if value == "":
            return None

        # TODO: ROUND/FORMAT DECIMALS

        return value

    def __update_extents(self, idx_x: int, idx_y: int, sheet_name: str, increment: bool):
        x_extent_list, y_extent_list = self.extents[sheet_name] 
        x_len = len(x_extent_list)
        y_len = len(y_extent_list)

        if increment == True:

            # if idx is out of bounds, extend list with 0's THEN increment
            if idx_x >= x_len:
                for i in range(0, idx_x + 1):
                    x_extent_list.append(0)
            x_extent_list[idx_x] += 1

            if idx_y >= y_len:
                for i in range(0, idx_y + 1):
                    y_extent_list.append(0)
            y_extent_list[idx_y] += 1
       
        else:
            # decrement self.extent_x
            x_extent_list[idx_x] -= 1
            y_extent_list[idx_y] -= 1

            i = 1
            while x_extent_list[x_len - i] == 0 and x_len - i > 0:
                x_extent_list.pop()
                i += 1
            
            i = 1
            while y_extent_list[y_len - i] == 0 and y_len - i > 0:
                y_extent_list.pop()
                i += 1

        self.extents[sheet_name] = (x_extent_list, y_extent_list)

                


if __name__ == "__main__":
    wb = Workbook()

    print(wb.new_sheet())
    print(wb.new_sheet("The Jimmy"))
    print(wb.new_sheet())
    print(wb.get_sheet_extent("The Jimmy"))
