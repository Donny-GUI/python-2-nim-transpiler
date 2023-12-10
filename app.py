import sys
import os

from util import replicate_directory_structure
from function_converter import FunctionConverter, convert_all_functions
from class_converter import ClassConverter, convert_all_classes
from import_fixer import get_imports
from postprocessing import var_assignment_for_integers, var_assignment_for_sequences, var_assignment_for_strings, fix_weird_double_quote
from signature_type_converter import fix_proc_types
from with_open_fixer import fix_nim_open_with 


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
import option

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
    print("[py2nim]: Fixing proc types assignment")
    fix_proc_types(newfile)
    print("[py2nim]: Fixing open with context managers")
    fix_nim_open_with(newfile)
    print("[py2nim]: Done!")

def convert_python_project():
    current_dir = os.getcwd()
    target_dir = replicate_directory_structure()
    for root, dirs, files in os.walk(os.path.join(current_dir, target_dir)):
        # unfinished
        pass


def application_entry():
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

    application_entry()
