import io
import re
import os
import ast 
import tokenize
import token
from keyword import kwlist, softkwlist
from typing import List, Dict, Any
import inspect



AllPythonTypes = [
    # Super-special typing primitives.
    'Annotated',
    'Any',
    'Callable',
    'ClassVar',
    'Concatenate',
    'Final',
    'ForwardRef',
    'Generic',
    'Literal',
    'Optional',
    'ParamSpec',
    'Protocol',
    'Tuple',
    'Type',
    'TypeVar',
    'TypeVarTuple',
    'Union',

    # ABCs (from collections.abc).
    'AbstractSet',  # collections.abc.Set.
    'ByteString',
    'Container',
    'ContextManager',
    'Hashable',
    'ItemsView',
    'Iterable',
    'Iterator',
    'KeysView',
    'Mapping',
    'MappingView',
    'MutableMapping',
    'MutableSequence',
    'MutableSet',
    'Sequence',
    'Sized',
    'ValuesView',
    'Awaitable',
    'AsyncIterator',
    'AsyncIterable',
    'Coroutine',
    'Collection',
    'AsyncGenerator',
    'AsyncContextManager',

    # Structural checks, a.k.a. protocols.
    'Reversible',
    'SupportsAbs',
    'SupportsBytes',
    'SupportsComplex',
    'SupportsFloat',
    'SupportsIndex',
    'SupportsInt',
    'SupportsRound',

    # Concrete collection types.
    'ChainMap',
    'Counter',
    'Deque',
    'Dict',
    'DefaultDict',
    'List',
    'OrderedDict',
    'Set',
    'FrozenSet',
    'NamedTuple',  # Not really a type.
    'TypedDict',  # Not really a type.
    'Generator',

    # Other concrete types.
    'BinaryIO',
    'IO',
    'Match',
    'Pattern',
    'TextIO',

    # One-off things.
    'AnyStr',
    'assert_type',
    'assert_never',
    'cast',
    'clear_overloads',
    'dataclass_transform',
    'final',
    'get_args',
    'get_origin',
    'get_overloads',
    'get_type_hints',
    'is_typeddict',
    'LiteralString',
    'Never',
    'NewType',
    'no_type_check',
    'no_type_check_decorator',
    'NoReturn',
    'NotRequired',
    'overload',
    'override',
    'ParamSpecArgs',
    'ParamSpecKwargs',
    'Required',
    'reveal_type',
    'runtime_checkable',
    'Self',
    'Text',
    'TYPE_CHECKING',
    'TypeAlias',
    'TypeGuard',
    'TypeAliasType',
    'Unpack',
]
# String Tokens
ConstantTokens = [
    "None", "False", "True", "__debug__", "NotImplemented"
]
SiteConstants = [
    "quit(", "exit(",
    "copyright", "credits", "licence"
]
KeywordTokens = [   
    "and",     
    "as",      
    "assert",  
    "async",   
    "await",   
    "break",   
    "class",   
    "continue",
    "def",     
    "del",     
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield"
]
BuiltinTokens = [
    "abs(",
    "aiter(",
    "all(",
    "anext(",
    "any(",
    "ascii(",
    "bin(",
    "bool(",
    "breakpoint(",
    "bytearray(",
    "bytes(",
    "callable(",
    "chr(",
    "classmethod(",
    "compile(",
    "complex(",
    "delattr(",
    "dict(",
    "dir(",
    "divmod(",
    "enumerate(",
    "eval(",
    "exec(",
    "filter(",
    "float(",
    "format(",
    "frozenset(",
    "getattr(",
    "globals(",
    "hasattr(",
    "hash(",
    "help(",
    "hex(",
    "id(",
    "input(",
    "int(",
    "isinstance(",
    "issubclass(",
    "iter(",
    "len(",
    "list(",
    "locals(",
    "map(",
    "max(",
    "memoryview(",
    "min(",
    "next(",
    "object(",
    "oct(",
    "open(",
    "ord(",
    "pow(",
    "print(",
    "property(",
    "range(",
    "repr(",
    "reversed(",
    "round(",
    "set(",
    "setattr(",
    "slice(",
    "sorted(",
    "staticmethod(",
    "str(",
    "sum(",
    "super(",
    "tuple(",
    "type(",
    "vars(",
    "zip(",
    "__import__("
]

# AST Arrays 
NodeNames = ["Expression","Interactive","FunctionType","Constant","FormattedValue","JoinedStr","List","Tuple","Set","Dict","Name","Load","Store","Del","Starred","Expr","UnaryOp","UAdd","USub","Not","Invert","BinOp","Add","Sub","Mult","Div","FloorDiv","Mod","Pow","LShift","RShift","BitOr","BitXor","BitAnd","MatMult","BoolOp","And","Or","Compare","Eq","NotEq","Lt","LtE","Gt","GtE","Is","IsNot","In","NotIn","Call","keyword","IfExp","Attribute","NamedExpr","Subscript","Slice","ListComp","SetComp","GeneratorExp","DictComp","comprehension","Assign","AnnAssign","AugAssign","Raise","Assert","Delete","Pass","Import","ImportFrom","alias","If","For","While","Break","Continue","Try","TryStar","ExceptHandler","With","withitem","Match","match_case","MatchValue","MatchSingleton","MatchSequence","MatchStar","MatchMapping","MatchClass","MatchAs","MatchOr","FunctionDef","Lambda","arguments","arg","Return","Yield","YieldFrom","Global","Nonlocal","ClassDef","AsyncFunctionDef","Await","AsyncFor","AsyncWith"]
NodeTypes = [ast.Expression, ast.Interactive, ast.FunctionType, ast.Constant, ast.FormattedValue, ast.JoinedStr, ast.List, ast.Tuple, ast.Set, ast.Dict, ast.Name, ast.Load, ast.Store, ast.Del, ast.Starred, ast.Expr, ast.UnaryOp, ast.UAdd, ast.USub, ast.Not, ast.Invert, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd, ast.MatMult, ast.BoolOp, ast.And, ast.Or, ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn, ast.Call, ast.keyword, ast.IfExp, ast.Attribute, ast.NamedExpr, ast.Subscript, ast.Slice, ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp, ast.comprehension, ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Raise, ast.Assert, ast.Delete, ast.Pass, ast.Import, ast.ImportFrom, ast.alias, ast.If, ast.For, ast.While, ast.Break, ast.Continue, ast.Try, ast.TryStar, ast.ExceptHandler, ast.With, ast.withitem, ast.Match, ast.match_case, ast.MatchValue, ast.MatchSingleton, ast.MatchSequence, ast.MatchStar, ast.MatchMapping, ast.MatchClass, ast.MatchAs, ast.MatchOr, ast.FunctionDef, ast.Lambda, ast.arguments, ast.arg, ast.Return, ast.Yield, ast.YieldFrom, ast.Global, ast.Nonlocal, ast.ClassDef, ast.AsyncFunctionDef, ast.Await, ast.AsyncFor, ast.AsyncWith]
NodeVector = [i for i in range(0, len(NodeTypes))]
DataclassTokens = [
    "int", "float", "str", "bool", "frozenset", "set", "dict", "complex", "memoryview"
]
DataTypeTokens = [
    "Int", "Float", "Str", "Bool", "Frozenset", "Set", "Dict", "Complex", "Memoryview"
]

# REGEX
FStringPattern = re.compile(r'f(["\']{1,3}).*?\1', re.DOTALL)
VariableDefinitonPattern = re.compile(r'\b\w+\s*=\s*.+')
KeywordPattern = re.compile(r'\b(?:' + '|'.join(KeywordTokens) + r')\b')
SoftKeyWordPattern = re.compile(r'\b(?:' + '|'.join(softkwlist) + r')\b')
FunctionDefinitionPattern = re.compile(r'\bdef\s+([a-zA-Z_]\w*)\s*\(')
DunderMainPattern = re.compile(r'^\s*if\s+__name__\s*==\s*["\']__main__["\']\s*:$', re.MULTILINE)
ClassPattern = re.compile(r'class\s+([a-zA-Z_]\w*)\s*:\s*(?:\n\s*def\s+([a-zA-Z_]\w*)\s*\([^)]*\):)?', re.MULTILINE)
FunctionPattern = re.compile(r'def\s+([a-zA-Z_]\w*)\s*\([^)]*\):(?:.*?)(?:(?=\bdef\b)|$)', re.DOTALL | re.MULTILINE)
all_patterns = [
    VariableDefinitonPattern,
    KeywordPattern,
    SoftKeyWordPattern,
    FunctionDefinitionPattern,
    DunderMainPattern,
    ClassPattern,
    FunctionPattern,
]

def convert_python_to_nim():

    with open("test.py", "r") as f:
        content = f.read()

    tokens = tokenize.tokenize(io.BytesIO(content.encode('utf-8')).readline)

    all_objects = []
    all_tokens = []
    lines = []
    lvl1_lines = []
    lvl1_tokens = []
    strings = []
    python_string = ""
    nim_string = ""

    for tok in tokens:
        lvl1_token = token.tok_name[tok.type]
        literal = tok.string
        lvl1_tokens.append(lvl1_token)
        strings.append(literal)
        all_objects.append(tok.string)
        all_tokens.append(token.tok_name[tok.type])
        
        if token.tok_name[tok.type] == "NEWLINE":
            lvl1_lines.append(lvl1_tokens)
            lvl1_tokens = []
            lines.append(strings)
            strings = []

    all_objects = list(set(all_objects))
    all_tokens = list(set(all_tokens))


    blocks = []
    string_blocks = []
    string_block = []
    block = []
    
    for index, line in enumerate(lvl1_lines):
        if line[0] == 'DEDENT':
            block.append(line)
            string_block.append(lines[index])
        else:
            blocks.append(line+block)
            block = []
            string_blocks.append(lines[index]+string_block)
            string_block = []

    for b in blocks:
        print("\n\n===============================")
        print(b)

    for sb in string_blocks:
        print("\n\n===============================")
        print(sb)


class TopLevelObject:
    def __init__(self, node, index) -> None:
        self.index = index
        self.node = node
        self.code = ast.unparse(node)

def new_top_level_object(ast_node: ast.Module, index: int ) -> TopLevelObject:
    return TopLevelObject(ast_node, index)

def get_module_filepath(module_name):
    try:
        module = __import__(module_name)
        filepath = getattr(module, "__file__", None)

        if filepath:
            # Convert to absolute path
            filepath = os.path.abspath(filepath)
            return filepath
        else:
            return f"Module '{module_name}' is not associated with a file."
    except ImportError as e:
        return f"Error: {e}"

def analyze_top_level_source(source: str, path: str):
    # get the python tree
    tree = ast.parse(source, filename=path, type_comments=True)
    # mode the body nodes iterable
    nodes = iter([node for node in tree.body])
    # prepare the results dict
    results: Dict[str, List[TopLevelObject]] = {}
    for index, node in enumerate(NodeNames):
        results[node] = []

    # go through all the nodes and classify them
    for i in range(len(source)):
        # get the next node
        try:
            node = next(nodes)
        except StopIteration:
            break
        # find out what type of node it is
        for index, item in enumerate(NodeTypes):
            if isinstance(node, item):
                # create a new TopLevelNode object
                results[NodeNames[index]].append(new_top_level_object(node, index))

    return results

def analyze_toplevel_python_code(filepath: str) -> Dict[str, List[Any]]:
    """
    Analyzes a Python file and extracts information about functions, classes, types,
    global variables, imports, and control statements.

    Args:
        filepath (str): The path to the Python file.

    Returns:
        Dict[str, List[Any]]: A dictionary containing the extracted information.
    """
    with open(filepath, 'r') as file:
        code = file.read()

    # get the python tree
    tree = ast.parse(code, filename=filepath, type_comments=True)
    # mode the body nodes iterable
    nodes = iter([node for node in tree.body])
    # prepare the results dict
    results: Dict[str, List[TopLevelObject]] = {}
    for index, node in enumerate(NodeNames):
        results[node] = []

    # go through all the nodes and classify them
    for i in range(len(code)):
        # get the next node
        try:
            node = next(nodes)
        except StopIteration:
            break
        # find out what type of node it is
        for index, item in enumerate(NodeTypes):
            if isinstance(node, item):
                # create a new TopLevelNode object
                results[NodeNames[index]].append(new_top_level_object(node, index))

    return results


def get_module_source(module_name):
    try:
        module = __import__(module_name)
        source_code = inspect.getsource(module)
        return source_code
    except ImportError as e:
        return f"Error: {e}"


def handle_import_of_standard_module(module_name: str):
    fp = get_module_filepath(module_name)
    source = get_module_source(module_name)
    if source.startswith("Error: "):
        print("An error occurred while importing another module: " + source)
        exit()
    
    python_blocks = analyze_top_level_source(module_name, fp)

    #### TODO   Finish the total imports section




def handle_imports(python_import_statements: list[TopLevelObject]) -> list[str]:
    nim_imports = []

    python_to_nim_imports = {
        "os": "os",                 # Python: import os
        "sys": "system",            # Python: import sys
        "json": "json",             # Python: import json
        "math": "math",             # Python: import math
        "cmath": "complex",         # Python: import cmath
        "collections": "sequtils",  # Python: import collections
        "heapq": "heapq",           # Python: import heapq
        "itertools": "iterators",   # Python: import itertools
        "functools": "functools",   # Python: import functools
        "random": "random",         # Python: import random
        "string": "strutils",       # Python: import string
        "re": "re",                 # Python: import re
        "datetime": "times",        # Python: import datetime
        "time": "times",            # Python: import time
        "calendar": "times",        # Python: import calendar
        "sysconfig": "os",          # Python: import sysconfig
        "subprocess": "process",    # Python: import subprocess
        "threading": "threading",   # Python: import threading
        "multiprocessing": "threading",  # Python: import multiprocessing
        "asyncio": "asyncdispatch",  # Python: import asyncio
        "socket": "net",            # Python: import socket
        "urllib": "httpclient",     # Python: import urllib
        "requests": "httpclient",   # Python: import requests
        "sqlite3": "db_sqlite",     # Python: import sqlite3
        "mysql": "db_mysql",        # Python: import mysql.connector
        "pandas": "nimpy_pandas",   # Python: import pandas
        "numpy": "nimpy_numpy",     # Python: import numpy
        "matplotlib": "nimpy_matplotlib",  # Python: import matplotlib
        # Add more mappings as needed
    }
    watchout_for = []
    for n in python_import_statements:
        bits = n.code.split(' ')
        if isinstance(n.node, ast.Import):
            mod = bits[-1]
            if mod not in python_to_nim_imports.keys():
                # import an entire nother source file   <<<<<<<
                nim_imports.append(f"import {mod}")
            else:
                nim_imports.append(f"import {python_to_nim_imports[bits[-1]]}")
            continue

        if isinstance(n.node, ast.ImportFrom):
            mod = python_to_nim_imports[bits[1]] if bits[1] in python_to_nim_imports.keys() else bits[1]
            
            if mod == bits[1]:
                # handle the complete import of another module
                pass

            nim_imports.append(f"import {mod}")
            add = False
            for index, item in enumerate(bits):
                if item == "import":
                    add = True
                    continue
                if add == True:
                    watchout_for.append(f"{bits[1]}.{item}")

    
    return nim_imports, watchout_for

def handle_classes(class_defs: list[TopLevelObject]) -> list[str]:
    nim_procs = []

    for class_def in class_defs:
        # Extract class name
        class_name = class_def.node.name

        # Create Nim proc definition for the constructor
        constructor_proc = f"proc {class_name}(): ref {class_name} ="

        # Create Nim proc definitions for each method
        method_procs = []
        for class_node in class_def.node.body:
            if isinstance(class_node, ast.FunctionDef):
                method_name = class_node.name
                pars = []
                for param in class_node.args.args:
                    if param.annotation.id == None:
                        newparam = param.arg + ": " + "nil"
                        pars.append(newparam)
                    else:
                        newparam = param.annotation.id
                        


                method_params = ', '.join([f"{param.arg}: {param.annotation.id}" for param in class_node.args.args])
                method_proc = f"proc {class_name}_{method_name}({method_params}):"
                method_procs.append(method_proc)

        # Combine constructor and method procs
        nim_class_procs = [constructor_proc] + method_procs

        # Join all Nim procedures into a single string
        nim_procs.append('\n'.join(nim_class_procs))

    return '\n\n'.join(nim_procs)

def main():
    python_blocks: dict[str:list] = analyze_toplevel_python_code("test.py")

    # make python all imports
    python_imports = list(python_blocks["Import"] + python_blocks["ImportFrom"])
    nim_imports = handle_imports(python_imports)

    nim_procs = handle_classes(python_blocks["ClassDef"])
