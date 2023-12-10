import ast


# python string module conversions
MandatoryStringImports = [
    "let asciiLetters: string = cstring.asciiLowercase & cstring.asciiUppercase",
    "let hexDigits: string = cstring.digits & cstring.asciiLowercase[10..15] & cstring.asciiUppercase[10..15]",
    "let octDigits: string = cstring.digits[0..7]",
    """let punctuation: string = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"""",
    'let whitespace: string = " \t\n\r\x0B\x0C"',
]

PythonStringConstants = {

    # ascii string constants
    "string.ascii_lowercase": "cstring.asciiLowercase",
    "string.ascii_uppercase": "cstring.asciiUppercase",
    "string.digits": "cstring.digits",
    "string.hexdigits": "hexDigits",
    "string.octdigits": "octDigits",
    "string.printable":"cstring.asciiPrintable",
    "string.whitespace": "whitespace",

}

def find_import_from_objects(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    tree = ast.parse(code)

    imported_objects = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_objects.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            for alias in node.names:
                imported_objects.add(f"{module}.{alias.name}")

    return imported_objects

