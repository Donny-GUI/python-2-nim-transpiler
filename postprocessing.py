from util import count_spaces_until_first_letter
import re
from lists import python_basic_types

NimPyTypeMap = {
    ": int = ": ": int = ",
    ": float = ": ": float = ",
    ": str = ": ": string = ",
    ": list = ": ": seq = ",
    ": tuple = ": ": tuple = ",
    ": dict = ": ": Table = ",
    ": set = ": ": set = ",
    ": bool = ": ": bool = ",
    ": bytes = ": ": seq[byte] = ",
    ": bytearray = ": ": seq[byte] = ",
    ": complex = ": ": complex = ",
    ": range = ": ": range = ",
    ": NoneType = ": ": nil = ",
    ": type = ": ": type = ",
    ": function = ": ": proc = ",
    ": module = ": ": Module = ",
    ": ellipsis = ": ": auto = ",
    ": NotImplementedType = ": ": NotImplemented = ",
    ": memoryview = ": ": MemoryView = ",
    ": slice = ": ": slice = ",
    ": frozenset = ": ": frozenSet = ",
    ": property = ": ": Property = ",
    ": super = ": ": Super = ",
    ": file = ": ": File = ",
    ": buffer = ": ": seq[byte] = ",
    ": long = ": ": int = ",
    ": unicode = ": ": string = ",
    ": basestring = ": ": string = ",
    ": xrange = ": ": range = ",
}

def print_all_nim_types():
    pycollections = ["list", "dict", "set"]
    nimcollections = ["seq", "Table", "set"]

    for coltype in pycollections:

        for ptype in python_basic_types:
            print(f'\t"{coltype}[{ptype}]",')
    
        print()
    

def fix_nil_default_types(filepath: str) -> None:
    with open(filepath, 'r') as file:
        lines = file.readlines()

    finds = ["int", "float", "bool", "string", "Table", "seq", "tuple", "set"]
    find_nils = [
        ": int = nil",
        ": float = nil",
        ": bool = nil",
        ": string = nil",
        ": Table = nil",
        ": seq = nil",
        ": tuple = nil",
        ": set = nil",
    ]
    replacements = [
        ": Option[int] = none[int]",
        ": Option[float] = none[float]",
        ": Option[bool] = none[bool]",
        ": Option[string] = none[string]",
        ": Option[Table] = none[Table]",
        ": Option[seq] = none[seq]",
        ": Option[tuple] = none[tuple]",
        ": Option[set] = none[set]",
    ]

    modified_lines = []
    for line in lines:
        if line.startswith('proc '):
            pass


def var_assignment_for_sequences(filepath:str):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    seq_pattern = re.compile(r"""^(\s*\w+\s*=\s*\@\[\]\s*)$""")

    for line in lines:
        match = seq_pattern.search(line)
        if match:
            assign_line = line.index("=")
            front = line[0:assign_line]
            sc = count_spaces_until_first_letter(front)
            space = sc * " "
            back = line[assign_line:]
            myline = space + "var " + front.strip() + ": seq " + back
            modified_lines.append(myline)
        else:
            modified_lines.append(line)

    with open(filepath, 'w') as file:
        file.writelines(modified_lines)

def var_assignment_for_strings(filepath:str):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    assignment_pattern = re.compile(r'(\w+)\s*=\s*("[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\')')

    for line in lines:
        match = assignment_pattern.search(line)
        if match:
            assign_line = line.index("=")
            front = line[0:assign_line]
            sc = count_spaces_until_first_letter(front)
            space = sc * " "
            back = line[assign_line:]
            myline = space + "var " + front.strip() + ": string " + back
            modified_lines.append(myline)
        else:
            modified_lines.append(line)

    with open(filepath, 'w') as file:
        file.writelines(modified_lines)

def var_assignment_for_integers(filepath: str):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    integer_literal_pattern = re.compile(r"""^(\s*\w+\s*=\s*\d+\s*)$""")
    names_found = []
    for index, line in enumerate(lines):
        match = integer_literal_pattern.search(line)
        if match:
            assign_line = line.index("=")
            front = line[0:assign_line]
            sc = count_spaces_until_first_letter(front)
            space = sc * " "
            back = line[assign_line:]
            name = front.strip()
            if len(names_found) > 0:
                lastidx, lastname = names_found[index-1]
                if lastname == name:
                    if index - lastidx > 10:
                        myline = space + "var " + name + ": int " + back
                        modified_lines.append(myline)
                        names_found.append([index, name])
                        continue
                myline = space + "var " + name + ": int " + back
                modified_lines.append(myline)
                names_found.append([index, name])
            else:
                myline = space + "var " + name + ": int " + back
                modified_lines.append(myline)
                names_found.append([index, name])
                continue
        else:
            modified_lines.append(line)
    
    with open(filepath, 'w') as file:
        file.writelines(modified_lines)
    
def fix_weird_double_quote(filepath: str):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    for line in lines:
        modified_lines.append(line.replace(' """"', ' ""'))
    with open(filepath, 'w') as file:
        file.writelines(modified_lines)
