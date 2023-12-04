import sys
import os

from function_converter import FunctionConverter, convert_all_functions
from class_converter import ClassConverter, convert_all_classes
from import_fixer import get_imports


def convert_python_source_to_nim_source(filepath: str, outfile:str=None):
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




def main():
    global opt_args

    if len(opt_args) == 1:
        if opt_args[0] == 'directory':
            for file in os.listdir():
                convert_python_source_to_nim_source(file)
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
