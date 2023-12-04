from class_converter import convert_all_classes
import os
import sys

PythonDirectory = os.path.dirname(sys.executable)


def extract_types_from_directory(directory: str=PythonDirectory):
    """
    Walks through a directory, finds Python files, and extracts types from each file.

    Parameters:
    - directory (str): Path to the directory.

    Returns:
    - dict: A dictionary mapping file names to sets of extracted types.
    """
    types_per_file = {}

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    converter = convert_all_classes(file_path)
                    types_per_file[file_path] = converter.type_definitions
                    print(file_path)
                    print(converter.type_definitions)
                except:
                    continue

    return types_per_file






