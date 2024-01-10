import unittest
import sys

sys.path.insert(0, "../sheets/")
from project1 import Workbook


# TB developed
class testWorkbook(unittest.TestCase):
    def test_init(self):
        print("Initiating Workbook tests")

    # def test_add_sheet(self):
    #     wb = Workbook()
    #     wb.add_sheet("test")
    #     print("Testing add_sheet")
    #     # self.assertEqual(, 1)


if __name__ == "__main__":
    wb = Workbook()

    # Sheet test: no input / identical names / case sensitivity test /
    # letters numbers and .?!,:;!@#$%^&*()-_ / test quote marks / empty string / space

    print(wb.new_sheet())
    print(wb.new_sheet("sheet1"))
    print(wb.new_sheet())
