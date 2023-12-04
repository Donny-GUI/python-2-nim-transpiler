import sys
import os
import re

from util import replicate_directory_structure
from function_converter import FunctionConverter, convert_all_functions
from class_converter import ClassConverter, convert_all_classes
from import_fixer import get_imports


def count_spaces_until_first_letter(input_string):
    space_count = 0
    for char in input_string:
        if char.isspace():
            space_count += 1
        else:
            break  # Exit loop when the first non-space character is encountered
    return space_count

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



def convert_python_source_to_nim_source(filepath: str, outfile:str=None) -> None:
    """
    Convert a python source file to a nim source file by path string

    Arguments:
        filepath (str): path to the file to convert
        outfile (str): path to the optional output file to write too.
    Returns: None
    """

    print("[py2nim]: Converting python source ", filepath)
    start_string = """\
import std/strutils
import tables

    \n"""
    print("[py2nim]: Getting imports...")
    import_strings = get_imports(filepath)
    if len(import_strings) != 0:
        start_string+="##  NonEssential Imports  ##\n"

    for impstr in import_strings:
        start_string += impstr + "\n"
    
    print("[py2nim]: Converting python classes to nim types...")
    class_converter: ClassConverter = convert_all_classes(filepath)
    print("[py2nim]: Assembling all methods and types...")
    string = class_converter.assemble()
    start_string+=string

    print("[py2nim]: Converting all functions....")
    func_converter: FunctionConverter = convert_all_functions(filepath)
    func_string = func_converter.assemble()
    start_string+=func_string

    print("[py2nim]: writing nim source...")
    bn = os.path.splitext(os.path.basename(filepath))[0]
    dn = os.path.dirname(filepath)
    bdn = os.path.basename(dn)

    newfile = dn + os.sep + bn + ".nim"
    if outfile == None:
        if newfile.startswith(os.sep):
            newfile = os.path.join(os.getcwd(), newfile[1:])
    else:
        newfile = outfile

    print("[py2nim]: saving ", newfile)
    with open(newfile, "w") as wfile:
        wfile.write(start_string)
    print("[py2nim]: Starting revisions...")
    print("[py2nim]: Fixing var assignments for strings")
    var_assignment_for_strings(newfile)
    print("[py2nim]: Fixing var assignments for integers")
    var_assignment_for_integers(newfile)
    print("[py2nim]: Fixing var assignments for lists")
    var_assignment_for_sequences(newfile)
    print("[py2nim]: Fixing double quote glitch...")
    fix_weird_double_quote(newfile)

    print("[py2nim]: Done!")

def convert_python_project():
    current_dir = os.getcwd()
    target_dir = replicate_directory_structure()
    for root, dirs, files in os.walk(os.path.join(current_dir, target_dir)):
        # unfinished
        pass




def main():
    global opt_args

    if len(opt_args) == 1:
        if opt_args[0] == 'directory':
            for file in os.listdir():
                convert_python_source_to_nim_source(file)
        elif opt_args[0] == "project":
            convert_python_project()
        else:
            for file in opt_args:
                if os.path.exists(file):
                    convert_python_source_to_nim_source(file)
                else:
                    print("[py2nim]: Cannot locate file: ", file)
    

if __name__ == "__main__":
    print("\n  Python to Nim Transpiler v1.1 \n")

    if len(sys.argv) > 1:
        opt_args = sys.argv[1:]
    else:
        print("[py2nim]: Please provide a file or use the 'directory' command \n\t  or the 'project' command to recursive convert")
        sys.exit()

    main()
