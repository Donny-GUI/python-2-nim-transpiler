import ast
import os

""" 
Create a way to walk through a python file finding lists inside of major nodes and prompting for there actions and types 

"""
MajorNodes = [
    ast.Module,
    ast.FunctionDef,
    ast.ClassDef,
]

MinorNodes = [
    ast.For,
    ast.While,
    ast.If,
    ast.With,
    ast.Assign,
    ast.ListComp,
    ast.Tuple,
    ast.Set,
    ast.Subscript,
    ast.Attribute,
    ast.Call,
    ast.List,
]

MajorListActions = [
    "Create a list",
    "Access a list element", 
    "Modify a list element",
    "Add Element(s) to a list",
    "Modify entire list"
]
CreateAListDescriptions = [
    "empty using '[]'",
    "empty using list()",
    "populated using literals",
    "populated using '[]*3' notation",
    "populated using list comprehension",
    "populated using list comprehension with conditional expression",
    "populated using named variables",
    "generated from a range of numbers",
]
AccessAListElementDescriptions = [
    "by index using .index method",
    "by index using [index] notation",
    "by value using .find method",
]
ModifyAListElementDescriptions = [
    "by index using [index] notation and setting it equal to a value",
    "removing element with del by index",
    "popping element with .pop method",
    "removing element by value with .remove method",
]
AddElementsToListDescriptions = [
    "appending using .append method",
    "extending using .extend method",
    "concatonate using + operator"
]
ModifyEntireListDescriptions = [
    "sorting list with .sort method",
    "reversing list with .reverse method",
    "slicing list with [0:1] notation",
]
ListDescriptions = [CreateAListDescriptions, 
                    AccessAListElementDescriptions, 
                    ModifyAListElementDescriptions, 
                    AddElementsToListDescriptions, 
                    ModifyEntireListDescriptions]


def get_python_nodes(filepath: str):
    with open(filepath, "r") as f:
        content = f.read()
    tree = ast.parse(content)
    return tree.body

def parse_minor_nodes(tree_body: list[ast.stmt]):
    return [node for node in tree_body if type(node) in MinorNodes]

def display_prompts(file:str, list_of_nodes: list[ast.stmt]) -> None:

    def iter_list_nodes(node: ast.AST):
        for n in ast.walk(node):
            if isinstance(n, ast.List):
                yield node
    
    def get_list_prompt(next_node):
        os.system("clear")
        string = ast.unparse(next_node)
        print(string)
        print("\n============================================================\n")
        print("\tWhat is happening with this list in this section of code?")
        for index, choice in enumerate(MajorListActions):
            print("\t  ", index + 1, ". ", choice)
        selection = input("[USER]:")
        return int(selection) - 1

    def get_description_prompt(choice: int):
        

    for node in list_of_nodes:
        lists_iter = iter_list_nodes(node)

        while True:
            try:
                nextnode = next(lists_iter)
            except StopIteration:
                break
            selection = get_list_prompt(nextnode)
            description = enumerate(ListDescriptions[selection])
            for index, desc in description:
                print("\t  ", index + 1, ". ", desc)






