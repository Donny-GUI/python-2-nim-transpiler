import os
import re
from tools import GREEN, RED, RESET


NilTypeReplacement = {
    ": int = nil": r": Option[int] = none[int]",
    ": float = nil": r": Option[float] = none[float]",
    ": str = nil": r": Option[string] = none[string]",
    ": list = nil": r": Option[seq] = none[seq]",
    ": tuple = nil": r": Option[tuple] = none[tuple]",
    ": dict = nil": r": Option[Table] = none[Table]",
    ": set = nil": r": Option[set] = none[set]",
    ": bool = nil": r": Option[bool] = none[bool]",
    ": bytes = nil": r": Option[seq[byte]] = none[seq[byte]]",
    ": bytearray = nil": r": Option[seq[byte]] = none[seq[byte]]",
    ": complex = nil": r": Option[complex] = none[complex]",
    ": range = nil": r": Option[range] = none[range]",
    ": NoneType = nil": r": Option[nil] = none[nil]",
    ": type = nil": r": Option[type] = none[type]",
    ": function = nil": r": Option[proc] = none[proc]",
    ": module = nil": r": Option[Module] = none[Module]",
    ": ellipsis = nil": r": Option[auto] = none[auto]",
    ": NotImplementedType = nil": r": Option[NotImplemented] = none[NotImplemented]",
    ": memoryview = nil": r": Option[MemoryView] = none[MemoryView]",
    ": slice = nil": r": Option[slice] = none[slice]",
    ": frozenset = nil": r": Option[frozenSet] = none[frozenSet]",
    ": property = nil": r": Option[Property] = none[Property]",
    ": super = nil": r": Option[Super] = none[Super]",
    ": file = nil": r": Option[File] = none[File]",
    ": buffer = nil": r": Option[seq[byte]] = none[seq[byte]]",
    ": long = nil": r": Option[int] = none[int]",
    ": unicode = nil": r": Option[string] = none[string]",
    ": basestring = nil": r": Option[string] = none[string]",
    ": xrange = nil": r": Option[range] = none[range]",
}

def replace_optional_string(input_string: str) -> str:
    pattern = r':\s*(\w+)\s*=\s*nil'
    replacement = r': Option[\1] = none[\1]'
    output_string = re.sub(pattern, replacement, input_string)
    return output_string

def replace_Liststr(inputstring: str) -> str:
    pattern = r':\s*List\[(\w+)\]\s*='
    replacement = r': seq[\1] ='
    return re.sub(pattern, replacement, inputstring)

def fix_proc_types(filepath: str):

    newlines = []
    
    with open(filepath, 'r') as f:
        lines = f.readlines()

    for line in lines:
        newline = line
        stripline = line.strip(" ")

        if stripline.startswith('proc ') or stripline.strip(" ").startswith("func "):
            aline = replace_optional_string(newline)
            newline = replace_Liststr(aline)

        newlines.append(newline)
    
    with open(filepath, 'w') as f:
        f.writelines(newlines)
    