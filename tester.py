import subprocess
from signature_type_converter import fix_proc_types
from universal_variables import PythonExampleDirectory, NimExampleDirectory
from class_converter import ClassConverter, convert_all_classes
from function_converter import FunctionConverter, convert_all_functions
import os


def make_nim_string(filepath: str):
    start_string = ""
    class_converter: ClassConverter = convert_all_classes(filepath)
    string = class_converter.assemble()
    start_string+=string
    func_converter: FunctionConverter = convert_all_functions(filepath)
    func_string = func_converter.assemble()
    start_string+=func_string

    return start_string

def print_nim_equivalent(example: str):
    nimexample = os.path.splitext(example)[0] + ".nim"
    fullpath = os.path.join(PythonExampleDirectory, example)
    nimstring = make_nim_string(fullpath)
    print(nimstring)
    nimfullpath = os.path.join(NimExampleDirectory, nimexample)
    with open(nimfullpath, "w") as wfile:
        wfile.write(nimstring)

    fix_proc_types(nimfullpath)
    
    output = evaluate_nim_file(nimfullpath)
    print(output)


def evaluate_nim_file(nimfullpath):
    run_command(nim_compile_command(nimfullpath))

def nim_compile_command(nim_filepath: str):
    return ["nim", "c", "-r", nim_filepath]

def run_command(command):
    try:
        # Run the command and capture the output
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        if result.stderr:
            return result.stderr
        return result

    except subprocess.CalledProcessError as e:
        # Handle errors if the command fails
        return e
    
def test_fib():
    print_nim_equivalent("fib.py")

test_fib()