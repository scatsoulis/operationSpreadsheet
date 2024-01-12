import unittest
import sys

# TB developed
class testWorkbook(unittest.TestCase):
    def test_init(self):
        print("Initiating Workbook tests")

    """
    def test_add_sheet(self):
        wb = Workbook()
        wb.add_sheet("test")
        print("Testing add_sheet")
        # self.assertEqual(, 1)
    
    def test_del_sheet(self):
        wb = Workbook()
        wb.add_sheet("test")
        wb.del_sheet("test")
        print("Testing del_sheet")
        # self.assertEqual(, 1)
    
    def test_list_sheets(self):
        wb = Workbook()
        wb.add_sheet("test")
        print("Testing list_sheets")
        # self.assertEqual(, 1)
        
        
    """
    


if __name__ == "__main__":
    wb = Workbook()

    # Sheet test: no input / identical names / case sensitivity test /
    # letters numbers and .?!,:;!@#$%^&*()-_ / test quote marks / empty string / space

    print(wb.new_sheet())
    print(wb.new_sheet("sheet1"))
    print(wb.new_sheet())
