import ast
from re import compile as regexCompile
from re import DOTALL, MULTILINE
from keyword import softkwlist


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
FStringPattern = regexCompile(r'f(["\']{1,3}).*?\1', DOTALL)
VariableDefinitonPattern = regexCompile(r'\b\w+\s*=\s*.+')
KeywordPattern = regexCompile(r'\b(?:' + '|'.join(KeywordTokens) + r')\b')
SoftKeyWordPattern = regexCompile(r'\b(?:' + '|'.join(softkwlist) + r')\b')
FunctionDefinitionPattern = regexCompile(r'\bdef\s+([a-zA-Z_]\w*)\s*\(')
DunderMainPattern = regexCompile(r'^\s*if\s+__name__\s*==\s*["\']__main__["\']\s*:$', MULTILINE)
ClassPattern = regexCompile(r'class\s+([a-zA-Z_]\w*)\s*:\s*(?:\n\s*def\s+([a-zA-Z_]\w*)\s*\([^)]*\):)?', MULTILINE)
FunctionPattern = regexCompile(r'def\s+([a-zA-Z_]\w*)\s*\([^)]*\):(?:.*?)(?:(?=\bdef\b)|$)', DOTALL | MULTILINE)
all_patterns = [
    VariableDefinitonPattern,
    KeywordPattern,
    SoftKeyWordPattern,
    FunctionDefinitionPattern,
    DunderMainPattern,
    ClassPattern,
    FunctionPattern,
]