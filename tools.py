import sys
import os
import ast
import time


RESET = '\033[0m'
BOLD = '\033[1m'
ITALIC = '\033[3m'
UNDERLINE = '\033[4m'
STRIKETHROUGH = '\033[9m'

# Foreground colors
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'

# Background colors
BLACK_BG = '\033[40m'
RED_BG = '\033[41m'
GREEN_BG = '\033[42m'
YELLOW_BG = '\033[43m'
BLUE_BG = '\033[44m'
MAGENTA_BG = '\033[45m'
CYAN_BG = '\033[46m'
WHITE_BG = '\033[47m'

def color_green(text):
    return GREEN_BG + text + RESET


def overprint(new_text):
    # Move the cursor up one line
    sys.stdout.write('\033[F')
    
    # Clear the line
    sys.stdout.write('\033[K')
    
    # Print the new text
    print(str(new_text))

    # Flush the output to ensure it's immediately written to the terminal
    sys.stdout.flush()

def extract_types_from_directory(directory):
    """
    Walks through a directory, finds Python files, and extracts types from each file.

    Parameters:
    - directory (str): Path to the directory.

    Returns:
    - dict: A dictionary mapping file names to sets of extracted types.
    """
    types_per_file = {}
    start_time = time.time()


    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                delta_time = str(time.time() - start_time)
                overprint("Extracting types from " + color_green(file_path) + " -> Time Elapsed: " + delta_time)
                try:
                    types = extract_types_from_file(file_path)
                    types_per_file[file] = types
                except:
                    continue

    return types_per_file

def extract_types_from_file(file_path):
    """
    Extracts types (classes, variables, etc.) used in a Python file.

    Parameters:
    - file_path (str): Path to the Python file.

    Returns:
    - set: A set containing the extracted types.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r') as file:
            code = file.read()

    # Parse the code using ast
    tree = ast.parse(code)

    # Extract types from the abstract syntax tree
    types = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Extract function arguments and their types
            for arg in node.args.args:
                if arg.annotation:
                    try:
                        types.add(arg.annotation.id)
                    except AttributeError as ae:
                        overprint("Attribute error")
                    
        elif isinstance(node, ast.AsyncFunctionDef):
            # Extract async function arguments and their types
            for arg in node.args.args:
                if arg.annotation:
                    try:
                        types.add(arg.annotation.id)
                    except AttributeError as ae:
                        overprint("Attribute error")

        elif isinstance(node, ast.ClassDef):
            # Extract class names
            types.add(node.name)

    return types