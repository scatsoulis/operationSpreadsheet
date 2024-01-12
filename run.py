import decimal
import sheets
import sys

# Should print the version number of your sheets library,
# which should be 1.0 for the first project.

# FIX:
# print(f"Using sheets engine version {sheets.version}")

# Make a new empty workbook
wb = sheets.Workbook()

# Create a couple sheets
(index1, name1) = wb.new_sheet()
(index2, name2) = wb.new_sheet()

# List sheets
print(wb.list_sheets())

# Delete first sheet and print new list
wb.del_sheet("Sheet2")
print(wb.list_sheets())

# Should print:  New spreadsheet "Sheet1" at index 0
print(f'New spreadsheet "{name1}" at index {index1}')

wb.set_cell_contents(name1, "a2", "12")
sys.exit()
wb.set_cell_contents(name1, "b1", "34")
wb.set_cell_contents(name1, "c1", "=a1+b1")


# value should be a decimal.Decimal('46')
value = wb.get_cell_value(name1, "c1")
assert value == decimal.Decimal("46")

# Should print:  c1 = 46
print(f"c1 = {value}")

wb.set_cell_contents(name1, "d3", "=nonexistent!b4")

# value should be a CellError with type BAD_REFERENCE
value = wb.get_cell_value(name1, "d3")
assert isinstance(value, sheets.CellError)
assert value.get_type() == sheets.CellErrorType.BAD_REFERENCE

# Cells can be set to error values as well
wb.set_cell_contents(name1, "e1", "#div/0!")
wb.set_cell_contents(name1, "e2", "=e1+5")
value = wb.get_cell_value(name1, "e2")
assert isinstance(value, sheets.CellError)
assert value.get_type() == sheets.CellErrorType.DIVIDE_BY_ZERO
