import os
from class_converter import ClassConverter, convert_all_classes
from import_fixer import get_imports


def convert_python_source_to_nim_source(filepath: str):
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
    print("[py2nim]: writing nim source...")
    bn = os.path.splitext(os.path.basename(filepath))[0]
    dn = os.path.dirname(filepath)
    newfile = dn + os.sep + bn + ".nim"
    if newfile.startswith(os.sep):
        newfile = os.path.join(os.getcwd(), newfile[1:])
    print("[py2nim]: saving ", newfile)
    with open(newfile, "w") as wfile:
        wfile.write(start_string)

