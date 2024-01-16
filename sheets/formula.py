# Formula parsing & evaluation
import decimal
import lark
from lark.visitors import visit_children_decor


class FormulaEvaluator(lark.visitors.Interpreter):
    def __init__(self) -> None:
        # self.formula = formula
        pass
    # @visit_children_decor
    def add_expr(self, tree):
        # Evaluate tree, evaluate sub-tree based on rules (self.visit_children)
        values = self.visit_children(tree) # decorator action (including arg)
        if values[1] == "+":
            return values[0] + values[2]
        elif values[1] == "-":
            return values[0] - values[2]
        else:
            raise RuntimeError(f"Unknown add_expr operator {values[1]}")
    
    # @visit_children_decor
    def mul_expr(self, tree):
        print("inside mult expression")
        values = self.visit_children(tree)
        if values[1] == "*":
            return values[0] * values[2]
        elif values[1] == "/":
            if values[2] == 0:  # May be caught earlier
                return decimal.Decimal("#DIV/0!")
            return values[0] / values[2]
        else:
            raise RuntimeError(f"Unknown mul_expr operator {values[1]}")

    # What ifs: if subtrees evaluate to string or cell error - what to do
    # Ok: if subtrees evaluate to number - return number
    #     if subtrees evaluate to string - use helper function to understand if number is within string
    #     if subtrees evaluate to cell error - propagate thru tree (just return error, else do math)

    # And take care of parentheses

    # And later (can do simple for part 1):
    # For cell update: only update affected cells (use dependency graph - if these change, replace dependency of particular cell)
    # Order of update: topological sort (update cells with least referencing, then those with further)
    # Checker: need to identify cycles in dep. graph (#CIRCREF!) - no hanging/crashing
    # Tarjan's algorithm (but improve on recursive nature)
    # Check slides

    def cell(self, tree):
        print("inside new cell")
        values = self.visit_children(tree)
        if len(tree.children) == 1: # Current sheet
            return self.data[tree.children[0]]
        if len(tree.children) == 2: # Different sheet
            return self.data[sheet_name][tree.children[1]]
            # return "!".join(tree.children)
        raise RuntimeError(f"Unknown cell reference {tree}")

    def number(self, tree):
        return decimal.Decimal(tree.children[0])

    def string(self, tree):
        return tree.children[0].value[1:-1]

    def parse(self, formula):
        print("inside parse")
        pass

    def evaluate(self, formula):
        pass


class CellRefFinder(lark.Visitor):
    def __init__(self) -> None:
        super().__init__()
        self.cell_refs = []

    def cell(self, tree):
        # print(tree.children)
        print("cell")
        print(tree)
        if len(tree.children) == 1:
            self.cell_refs.append(str(tree.children[0]))
        else:
            assert len(tree.children) == 2
            self.cell_refs.append("!".join(tree.children))


class CalculateTree(lark.Transformer):
    # For now - for part 4 this is too coarse - simple bottom-up traversal will be slow
    # (need if condition to evaluate the right expression, this via Interpreter).
    from operator import add, sub, mul, truediv as div, neg

    number = float

    def __init__(self) -> None:
        super().__init__()
        self.formula = Formula()




# visit_children()
# @visit_children_decor
        

class CellDependencyGraph():
    def __init__(self):
        self.graph = {}

# create dictionary of format {sheet_name: {cell: [dependencies]}, }
    def get_dependency(self, curr_sheet, curr_cell):
        return self.graph[curr_sheet][curr_cell]
           
    def set_dependency(self, curr_sheet, curr_cell, dependency):
        if curr_sheet not in self.graph:
            self.graph[curr_sheet] = {}
        sheet_dict = self.graph[curr_sheet]
        if curr_cell not in sheet_dict:
            sheet_dict[curr_cell] = []
        sheet_dict[curr_cell] += dependency
        return
    
    # when the formula is changed
    def clear_dependency(self, curr_sheet, curr_cell):
        self.graph[curr_sheet][curr_cell] = []
        return
    
    # may be a problem if 1 goes to 2 and 4 and 2 goes to 4
    def top_sort(self, sheet_name, curr_cell):
        visited = set()
        result = []
        def dfs(sheet_name, curr_cell):
            visited.add(curr_cell)
            for dependency in self.graph[sheet_name][curr_cell]:
                if dependency not in visited:
                    # hasSheetName checks if the sheetname is in the cell information
                    if hasSheetName(dependency):
                        # if sheet name is in the cell information, then splits the cell name into sheet name and cell number
                        sheet_name, dependency = splitCellName(dependency)
                    dfs(sheet_name, dependency)
                else:
                    # THIS IS WHERE CYCLE IS DETECTED, RAISE ERROR
                    raise RuntimeError(f"Cycle detected in cell dependency graph")

                result.append(curr_cell)

        
        dfs(sheet_name, curr_cell)
        return result[::-1]
    
        

        

if __name__ == "__main__":
    # Creating lark parser (second stage)
    parser = lark.Lark.open("formulas.lark", start="formula", rel_to=__file__)

    # Creating tree
    curr_sheet = "Sheet1"
    curr_cell = "b1"
    tree = parser.parse("= a1 + 3 * Sheet2!A2")
    # Notes: Matches lower & uppercase sheetnames (e.g. turn em all uppercase)
    # Notes: Try to match sheetnames for cell that aren't referenced (prob home sheet)
    print("the tree")
    print(tree.pretty())

    v = CellRefFinder()
    print("inside")
    print(v.cell_refs)
    print("finished inside")
    v.visit(tree)
    print("inside2")
    print(v.cell_refs)
    print("inside3")
    print(type(v.cell_refs))


    print("Generating dependency graph")
    d = CellDependencyGraph()
    d.set_dependency("Sheet1", "a1", v.cell_refs)
    d.set_dependency("Sheet1", "a1", "3")
    print(d.get_dependency("Sheet1", "a1"))




    """
    parser = lark.Lark.open("formulas.lark", start="formula", rel_to=__file__)
    evaluator = FormulaEvaluator()

    tree = parser.parse("=123.456")
    value = evaluator.visit(tree)
    print(f"value = {value} (type is {type(value)})")

    tree = parser.parse('="Cheers!"')
    value = evaluator.visit(tree)
    print(f"value = {value} (type is {type(value)})")

    tree = parser.parse("=3/4")
    print(tree.pretty())
    value = evaluator.visit(tree)
    print(f"value = {value} (type is {type(value)})")
    """
