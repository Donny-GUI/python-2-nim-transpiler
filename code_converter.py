import ast



# TODO LIST
# 1. CodeConverter.convert_await
# 2. CodeConverter.convert_yield
# 3. CodeConverter.convert_yield_from
# 4. CodeConverter.convert_starred
# 5. CodeConverter.convert_try_star


def name(anyclass: any) -> str:
    return anyclass.__name__

def attributes(anyclass: any) -> list[str]:
    return [attr for attr in vars(anyclass) if not callable(getattr(anyclass, attr)) and not attr.startswith("__")]

def properties(anyclass: any) -> list[str]:
    
    def make_instance(anyclass, args=0):
        if args != 0:
            values = None*args
            try:
                instance = anyclass(*values)
            except:
                instance = make_instance(anyclass, args+1)
            finally:
                return instance
        else:
            try:
                instance = anyclass()
            except:
                instance = make_instance(anyclass, args+1)
            finally:
                return instance
        
    my_instance = make_instance(anyclass)

    all_attributes = dir(my_instance)
    return [attr for attr in all_attributes if not callable(getattr(my_instance, attr)) and not attr.startswith("__")]

def convert_subscript_to_nim(node):
    if not isinstance(node, ast.Subscript):
        raise ValueError("Input must be an ast.Subscript node")

    value = convert_expr_to_nim(node.value)
    slice_expr = convert_slice_to_nim(node.slice)

    return f"{value}[{slice_expr}]"

def convert_slice_to_nim(slice_node):
    if isinstance(slice_node, ast.Index):
        return convert_expr_to_nim(slice_node.value)
    elif isinstance(slice_node, ast.Slice):
        lower = convert_expr_to_nim(slice_node.lower) if slice_node.lower else ""
        upper = convert_expr_to_nim(slice_node.upper) if slice_node.upper else ""
        step = convert_expr_to_nim(slice_node.step) if slice_node.step else ""
        return f"{lower}:{upper}:{step}"
    else:
        pass
        #raise ValueError(f"Unsupported slice node: {type(slice_node).__name__}")

def convert_keyword_to_nim(keyword):
    return f"{keyword.arg} = {convert_expr_to_nim(keyword.value)}"

def convert_cmpop_to_nim(cmpop_node):
    if isinstance(cmpop_node, ast.Eq):
        return "=="
    elif isinstance(cmpop_node, ast.NotEq):
        return "!="
    elif isinstance(cmpop_node, ast.Lt):
        return "<"
    elif isinstance(cmpop_node, ast.LtE):
        return "<="
    elif isinstance(cmpop_node, ast.Gt):
        return ">"
    elif isinstance(cmpop_node, ast.GtE):
        return ">="
    # Add more comparison operators as needed
    else:
        raise ValueError(f"Unsupported comparison operator node: {type(cmpop_node).__name__}")

def convert_setcomp_to_nim(node):
    if not isinstance(node, ast.SetComp):
        raise ValueError("Input must be an ast.SetComp node")

    target = convert_expr_to_nim(node.elt)
    generators = [convert_comprehension_to_nim(generator) for generator in node.generators]

    return f"{{ {target} {generators} }}"

def convert_comprehension_to_nim(generator):
    target = convert_expr_to_nim(generator.target)
    iter_expr = convert_expr_to_nim(generator.iter)
    ifs = [f"if {convert_expr_to_nim(iff)}" for iff in generator.ifs]

    return f"for {target} in {iter_expr} {ifs}"

def convert_joinedstr_to_nim(node):
    if not isinstance(node, ast.JoinedStr):
        raise ValueError("Input must be an ast.JoinedStr node")

    parts = [convert_expr_to_nim(value) if isinstance(value, ast.FormattedValue) else str(value.s) for value in node.values]
    return f'"{"".join(parts)}"'

def convert_formattedvalue_to_nim(node):
    if not isinstance(node, ast.FormattedValue):
        raise ValueError("Input must be an ast.FormattedValue node")

    value = convert_expr_to_nim(node.value)
    format_spec = node.format_spec

    if format_spec is not None:
        format_spec_str = convert_expr_to_nim(format_spec)
        return f'"{value, {format_spec_str}}"'
    else:
        return f'"{value}"'

def convert_namedexpr_to_nim(node):
    if not isinstance(node, ast.NamedExpr):
        raise ValueError("Input must be an ast.NamedExpr node")

    target = convert_expr_to_nim(node.target)
    value = convert_expr_to_nim(node.value)

    return f"{target} = {value}"

def convert_attribute_to_nim(node):
    if not isinstance(node, ast.Attribute):
        raise ValueError("Input must be an ast.Attribute node")

    value = convert_expr_to_nim(node.value)
    attr = node.attr

    return f"{value}.{attr}"

def convert_starred_to_nim(node):
    if not isinstance(node, ast.Starred):
        raise ValueError("Input must be an ast.Starred node")

    value = convert_expr_to_nim(node.value)

    return f"@{value}"

def convert_list_to_nim(node):
    if not isinstance(node, ast.List):
        raise ValueError("Input must be an ast.List node")

    elements = [convert_expr_to_nim(elem) for elem in node.elts]
    nim_list = f"seq[{', '.join(elements)}]"

    return nim_list

def convert_tuple_to_nim(node):
    if not isinstance(node, ast.Tuple):
        raise ValueError("Input must be an ast.Tuple node")

    elements = [convert_expr_to_nim(elem) for elem in node.elts]
    nim_tuple = f"({', '.join(elements)})"

    return nim_tuple

def convert_asyncfunctiondef_to_nim(node):
    if not isinstance(node, ast.AsyncFunctionDef):
        raise ValueError("Input must be an ast.AsyncFunctionDef node")

    # Async function name
    function_name = node.name

    # Async function parameters
    parameters = [convert_arg_to_nim(arg) for arg in node.args.args]
    parameters_str = ', '.join(parameters)

    # Return type (if specified)
    return_type = ""
    if node.returns:
        return_type = f": {convert_expr_to_nim(node.returns)}"

    # Async function body
    body = convert_body_to_nim(node.body)

    # Combine components to form the Nim async function
    asy = "{.async.}"
    nim_async_function = f"proc {function_name}({parameters_str}){return_type} {asy} =\n"
    nim_async_function += body

    return nim_async_function

def convert_classdef_to_nim(node):
    if not isinstance(node, ast.ClassDef):
        raise ValueError("Input must be an ast.ClassDef node")

    # Class name
    class_name = node.name

    # Base classes
    base_classes = [convert_expr_to_nim(base) for base in node.bases]
    base_classes_str = ', '.join(base_classes)

    # Class attributes and methods
    class_body = convert_classbody_to_nim(node.body)

    # Combine components to form the Nim class
    nim_class = f"type {class_name} = object of {base_classes_str}\n"
    nim_class += class_body

    return nim_class

def convert_classbody_to_nim(body_nodes):
    return "\n".join([convert_classstmt_to_nim(stmt) for stmt in body_nodes])

def convert_classstmt_to_nim(stmt_node):
    if isinstance(stmt_node, ast.FunctionDef):
        return convert_method_to_nim(stmt_node)
    elif isinstance(stmt_node, ast.AsyncFunctionDef):
        return convert_method_to_nim(stmt_node, is_async=True)
    elif isinstance(stmt_node, ast.Assign):
        return convert_attribute_to_nim(stmt_node)
    else:
        raise ValueError(f"Unsupported class statement node: {type(stmt_node).__name__}")

def convert_method_to_nim(node, is_async=False):
    # Method name
    method_name = node.name

    # Method parameters
    parameters = [convert_arg_to_nim(arg) for arg in node.args.args]
    parameters_str = ', '.join(parameters)

    # Return type (if specified)
    return_type = ""
    if node.returns:
        return_type = f": {convert_expr_to_nim(node.returns)}"

    # Method body
    body = convert_body_to_nim(node.body)

    # Combine components to form the Nim method
    method_prefix = "proc" if not is_async else "proc {.async.}"
    nim_method = f"{method_prefix} {method_name}({parameters_str}){return_type} =\n"
    nim_method += body

    return nim_method

def convert_attribute_to_nim(node):
    # Attribute name
    attribute_name = convert_expr_to_nim(node.value)

    # Attribute value (for simplicity, assumes a single value)
    attribute_value = convert_expr_to_nim(node.value)

    # Combine components to form the Nim attribute
    nim_attribute = f"{attribute_name} = {attribute_value}"

    return nim_attribute

def convert_functiondef_to_nim(node):
    if not isinstance(node, ast.FunctionDef):
        raise ValueError("Input must be an ast.FunctionDef node")

    # Function name
    function_name = node.name

    # Function parameters
    parameters = [convert_arg_to_nim(arg) for arg in node.args.args]
    parameters_str = ', '.join(parameters)

    # Return type (if specified)
    return_type = ""
    if node.returns:
        return_type = f": {convert_expr_to_nim(node.returns)}"

    # Function body
    body = convert_body_to_nim(node.body)

    # Combine components to form the Nim function
    nim_function = f"proc {function_name}({parameters_str}){return_type} =\n"
    nim_function += body

    return nim_function

def convert_arg_to_nim(arg_node):
    if isinstance(arg_node, ast.arg):
        return arg_node.arg
    else:
        raise ValueError("Unsupported argument node")

def convert_body_to_nim(body_nodes):
    return "\n".join([convert_stmt_to_nim(stmt) for stmt in body_nodes])

def convert_asyncfor_to_nim(node):
    if not isinstance(node, ast.AsyncFor):
        raise ValueError("Input must be an ast.AsyncFor node")

    target = convert_expr_to_nim(node.target)
    iterable = convert_expr_to_nim(node.iter)
    body = convert_body_to_nim(node.body)

    nim_asyncfor_loop = f"for {target} in {iterable}.itemsAsync():\n"
    nim_asyncfor_loop += body

    return nim_asyncfor_loop


def convert_stmt_to_nim(stmt_node):

    if isinstance(stmt_node, ast.Expr):
        return convert_expr_to_nim(stmt_node.value)
    elif isinstance(stmt_node, ast.Return):
        x = f"result = {convert_expr_to_nim(stmt_node.value)}"
        
        return x
    elif isinstance(stmt_node, ast.Assign):
        return convert_assign_to_nim(stmt_node)
    elif isinstance(stmt_node, ast.FunctionDef):
        return convert_functiondef_to_nim(stmt_node)
    elif isinstance(stmt_node, ast.If):
        return convert_if_to_nim(stmt_node)
    elif isinstance(stmt_node, ast.Try):
        return convert_try_to_nim(stmt_node)
    elif stmt_node.value == None:
        return "nil"
    else:
        raise ValueError(f"Unsupported statement node: {type(stmt_node).__name__}")

def convert_assign_to_nim(node):
    if not isinstance(node, ast.Assign):
        raise ValueError("Input must be an ast.Assign node")
    if isinstance(node.value, ast.Constant):
        return convert_constant_to_nim(node)
    
    targets = []
    for x in node.targets:
        if isinstance(x, ast.Constant):
            targets.append(convert_constant_to_nim(x))
        else:
            targets.append(convert_expr_to_nim(x))
    values = []

    if isinstance(node.value, ast.IfExp):
        return
    
    if isinstance(node.value, ast.BinOp):
        return str(node.value)
    
    for value in node.value.elts:
        try: 
            values.append(convert_expr_to_nim(value))
        except AttributeError:
            if isinstance(value, ast.Constant):
                values.append(convert_constant_to_nim(value))


    nim_assignments = []
    for target, value in zip(targets, values):
        nim_assignment = f"{target} = {value}"
        nim_assignments.append(nim_assignment)

    return "\n".join(nim_assignments)

def convert_augassign_to_nim(node):
    if not isinstance(node, ast.AugAssign):
        raise ValueError("Input must be an ast.AugAssign node")

    target = convert_expr_to_nim(node.target)
    value = convert_expr_to_nim(node.value)
    op = convert_op_to_nim(node.op)

    nim_assignment = f"{target} {op}= {value}"

    return nim_assignment

def convert_annassign_to_nim(node):
    if not isinstance(node, ast.AnnAssign):
        raise ValueError("Input must be an ast.AnnAssign node")

    target = convert_expr_to_nim(node.target)
    annotation = convert_expr_to_nim(node.annotation)
    value = convert_expr_to_nim(node.value) if node.value else ""

    nim_assignment = f"{target}: {annotation} = {value}"

    return nim_assignment

def convert_for_to_nim(node):
    if not isinstance(node, ast.For):
        raise ValueError("Input must be an ast.For node")

    target = convert_expr_to_nim(node.target)
    iterable = convert_expr_to_nim(node.iter)
    body = convert_body_to_nim(node.body)

    nim_for_loop = f"for {target} in {iterable}:\n"
    nim_for_loop += body

    return nim_for_loop

def convert_while_to_nim(node):
    if not isinstance(node, ast.While):
        raise ValueError("Input must be an ast.While node")

    test = convert_expr_to_nim(node.test)
    body = convert_body_to_nim(node.body)

    nim_while_loop = f"while {test}:\n"
    nim_while_loop += body

    return nim_while_loop

def convert_compare_to_nim(compare_node):
    left = convert_expr_to_nim(compare_node.left)
    right = convert_expr_to_nim(compare_node.comparators[0])
    op = convert_cmpop_to_nim(compare_node.ops[0])

    return f"({left} {op} {right})"

def convert_cmpop_to_nim(cmpop_node):
    if isinstance(cmpop_node, ast.Eq):
        return "=="
    elif isinstance(cmpop_node, ast.NotEq):
        return "!="
    elif isinstance(cmpop_node, ast.Lt):
        return "<"
    elif isinstance(cmpop_node, ast.LtE):
        return "<="
    elif isinstance(cmpop_node, ast.Gt):
        return ">"
    elif isinstance(cmpop_node, ast.GtE):
        return ">="
    # Add more comparison operators as needed
    else:
        raise ValueError(f"Unsupported comparison operator node: {type(cmpop_node).__name__}")

def convert_if_to_nim(node):
    if not isinstance(node, ast.If):
        raise ValueError("Input must be an ast.If node")

    test = convert_expr_to_nim(node.test)
    body = convert_body_to_nim(node.body)

    nim_if_statement = f"if {test}:\n"
    nim_if_statement += body

    if node.orelse:
        orelse = convert_orelse_to_nim(node.orelse)
        nim_if_statement += orelse

    return nim_if_statement

def convert_orelse_to_nim(orelse_nodes):
    if not orelse_nodes:
        return ""

    if isinstance(orelse_nodes[0], ast.If):
        return convert_if_to_nim(orelse_nodes[0])
    else:
        return "else:\n" + convert_body_to_nim(orelse_nodes)

def convert_with_to_nim(node):
    if not isinstance(node, ast.With):
        raise ValueError("Input must be an ast.With node")

    context_expr = convert_expr_to_nim(node.context_expr)
    body = convert_body_to_nim(node.body)

    nim_with_statement = f"with {context_expr}:\n"
    nim_with_statement += body

    return nim_with_statement

def convert_asyncwith_to_nim(node):
    if not isinstance(node, ast.AsyncWith):
        raise ValueError("Input must be an ast.AsyncWith node")

    context_expr = convert_expr_to_nim(node.context_expr)
    body = convert_body_to_nim(node.body)

    nim_asyncwith_statement = f"await {context_expr}:\n"
    nim_asyncwith_statement += body

    return nim_asyncwith_statement

def convert_raise_to_nim(node):
    if not isinstance(node, ast.Raise):
        raise ValueError("Input must be an ast.Raise node")

    if node.exc is not None:
        exc_type = convert_expr_to_nim(node.exc)
        nim_raise_statement = f"raise {exc_type}"
    else:
        nim_raise_statement = "raise"

    if node.cause is not None:
        cause = convert_expr_to_nim(node.cause)
        nim_raise_statement += f", {cause}"

    return nim_raise_statement

def convert_try_to_nim(node):
    if not isinstance(node, ast.Try):
        raise ValueError("Input must be an ast.Try node")

    body = convert_body_to_nim(node.body)
    excepts = convert_excepts_to_nim(node.handlers)
    orelse = convert_body_to_nim(node.orelse)
    finalbody = convert_body_to_nim(node.finalbody)

    nim_try_statement = f"try:\n{body}"

    if excepts:
        nim_try_statement += f"\n{excepts}"

    if orelse:
        nim_try_statement += f"\nelse:\n{orelse}"

    if finalbody:
        nim_try_statement += f"\nfinally:\n{finalbody}"

    return nim_try_statement

def convert_excepts_to_nim(handlers):
    if not handlers:
        return ""

    nim_excepts = []
    for handler in handlers:
        except_type = convert_expr_to_nim(handler.type)
        except_body = convert_body_to_nim(handler.body)
        nim_except = f"except {except_type}:\n{except_body}"
        nim_excepts.append(nim_except)

    return "\n".join(nim_excepts)

def convert_assert_to_nim(node):
    if not isinstance(node, ast.Assert):
        raise ValueError("Input must be an ast.Assert node")

    test = convert_expr_to_nim(node.test)
    msg = convert_expr_to_nim(node.msg) if node.msg is not None else ""

    nim_assert_statement = f"assert {test}, {msg}"

    return nim_assert_statement

def convert_import_to_nim(node):
    if not isinstance(node, ast.Import):
        raise ValueError("Input must be an ast.Import node")

    nim_import_statements = []

    for alias in node.names:
        module_name = convert_alias_to_nim(alias)
        nim_import_statements.append(f"import {module_name}")

    return "\n".join(nim_import_statements)

def convert_alias_to_nim(alias):
    if alias.asname is not None:
        return f"{alias.name} as {alias.asname}"
    else:
        return alias.name

def convert_target_to_nim(node):
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Call):
        return convert_call_to_nim(node)
    else:
        raise ValueError(f"Unsupported target node: {type(node).__name__}")

def convert_ast_node_to_nim(node):
    if isinstance(node, ast.BinOp):
        left = convert_ast_node_to_nim(node.left)
        right = convert_ast_node_to_nim(node.right)
        op = convert_op_to_nim(node.op)
        return f"({left} {op} {right})"
    elif isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Constant):
        return str(node.value)
    elif isinstance(node, ast.Call):
        return convert_call_to_nim(node)
    # Add more cases as needed for other expression types
    elif isinstance(node, ast.Attribute):
        return convert_attribute_to_nim(node)
    else:
        raise ValueError(f"Unsupported expression node: {type(node).__name__}")

def convert_listcomp_to_nim(node):
    if not isinstance(node, ast.ListComp):
        raise ValueError("Input must be an ast.ListComp node")

    target = node.elt
    generators = node.generators

    nim_code = "var result: seq["
    nim_code += convert_ast_node_to_nim(target)
    nim_code += "]\n"

    for generator in generators:
        nim_code += "for "
        nim_code += convert_target_to_nim(generator.target)
        nim_code += " in "
        nim_code += convert_ast_node_to_nim(generator.iter)
        nim_code += ":\n"

    nim_code += "  result.add("
    nim_code += convert_ast_node_to_nim(target)
    nim_code += ")\n"

    return nim_code

def convert_importfrom_to_nim(node):
    if not isinstance(node, ast.ImportFrom):
        raise ValueError("Input must be an ast.ImportFrom node")

    module_name = convert_module_to_nim(node)
    imported_names = convert_imported_names_to_nim(node.names)

    nim_importfrom_statement = f"from {module_name} import {imported_names}"

    return nim_importfrom_statement

def convert_module_to_nim(node):
    module_name = node.module
    if node.level > 0:
        module_name = "." * node.level + module_name

    return module_name

def convert_imported_names_to_nim(names):
    nim_imported_names = []

    for alias in names:
        nim_imported_names.append(convert_alias_to_nim(alias))

    return ", ".join(nim_imported_names)

def convert_lambda_to_nim(node):

    parameters = ", ".join(param.arg for param in node.args.args)
    nim_lambda = f"proc ({parameters}): "
    
    body = convert_expr_to_nim(node.body)
    nim_lambda += f"{body}"

    return nim_lambda

def convert_constant_to_nim(node):
    if node.value == None:
        return "nil"


    value = node.value
    nim_literal = convert_value_to_nim_literal(value)


    return nim_literal

def convert_value_to_nim_literal(value):
    lit = ast.unparse(value)

    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    elif value.value == None:
        return "nil"
    elif value is None:
        return "nil"
    elif value.value == 0:
        return "0"
    elif lit == "''" or value.value == "''":
        return "''"
    else:
        raise ValueError(f"Unsupported constant value: {value}")

def convert_generatorexp_to_nim(node):
    if not isinstance(node, ast.GeneratorExp):
        raise ValueError("Input must be an ast.GeneratorExp node")

    target = node.elt
    generators = node.generators

    nim_code = "iterator "
    nim_code += convert_target_to_nim(target)
    nim_code += f"():\n"

    for generator in generators:
        nim_code += "  for "
        nim_code += convert_target_to_nim(generator.target)
        nim_code += " in "
        nim_code += convert_ast_node_to_nim(generator.iter)
        nim_code += ":\n"

    nim_code += "    yield "
    nim_code += convert_ast_node_to_nim(target)

    return nim_code

def convert_expr_to_nim(expr_node):
    if isinstance(expr_node, ast.BinOp):
        return f"({convert_expr_to_nim(expr_node.left)} {convert_op_to_nim(expr_node.op)} {convert_expr_to_nim(expr_node.right)})"
    elif isinstance(expr_node, ast.Name):
        return expr_node.id
    elif isinstance(expr_node, ast.Constant):
        return str(expr_node.value)
    elif isinstance(expr_node, ast.SetComp):
        return convert_setcomp_to_nim(expr_node)
    elif isinstance(expr_node, ast.Call):
        return convert_call_to_nim(expr_node)
    elif isinstance(expr_node, ast.JoinedStr):
        return convert_joinedstr_to_nim(expr_node)
    elif isinstance(expr_node, ast.FormattedValue):
        return convert_formattedvalue_to_nim(expr_node)
    elif isinstance(expr_node, ast.NamedExpr):
        return convert_namedexpr_to_nim(expr_node)
    elif isinstance(expr_node, ast.Attribute):
        return convert_attribute_to_nim(expr_node)
    elif isinstance(expr_node, ast.Subscript):
        return convert_subscript_to_nim(expr_node)
    elif isinstance(expr_node, ast.Starred):
        return convert_starred_to_nim(expr_node)
    elif isinstance(expr_node, ast.List):
        return convert_list_to_nim(expr_node)
    elif isinstance(expr_node, ast.Tuple):
        return convert_tuple_to_nim(expr_node)
    elif isinstance(expr_node, ast.Compare):
        return convert_compare_to_nim(expr_node)
    elif isinstance(expr_node, ast.Lambda):
        return convert_lambda_to_nim(expr_node)
    elif isinstance(expr_node, ast.ListComp):
        return convert_listcomp_to_nim(expr_node)
    elif isinstance(expr_node, ast.GeneratorExp):
        return convert_generatorexp_to_nim(expr_node)
    
    
    
    
    else:
        raise ValueError(f"Unsupported expression node: {type(expr_node).__name__}")
    
def convert_call_to_nim(node):
    if not isinstance(node, ast.Call):
        raise ValueError("Input must be an ast.Call node")

    func = convert_expr_to_nim(node.func)
    args = [convert_expr_to_nim(arg) for arg in node.args]
    keywords = [convert_keyword_to_nim(kw) for kw in node.keywords]

    nim_args = ', '.join(args + keywords)
    return f"{func}({nim_args})"

def convert_op_to_nim(op_node):
    if isinstance(op_node, ast.Add):
        return "+"
    elif isinstance(op_node, ast.Sub):
        return "-"
    elif isinstance(op_node, ast.Mult):
        return "*"
    elif isinstance(op_node, ast.Div):
        return "/"
    # Add more operators as needed
    else:
        raise ValueError(f"Unsupported operator node: {type(op_node).__name__}")
    
class CodeConverter(object):
    def __init__(self) -> None:
        self.lines = []
        self.last_node = None
        self.node = None
        self.discard = 0
        self.nim_value = ""

    def convert_bool_op(self, node: ast.BoolOp):
        if isinstance(node, ast.BoolOp):
            op = 'and' if isinstance(node.op, ast.And) else 'or'
            return f"{op.join(self.convert_bool_op(value) for value in node.values)}"
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Compare):
            left = self.convert_bool_op(node.left)
            ops = " ".join(f"{op.op} {self.convert_bool_op(comparator)}" for op, comparator in zip(node.ops, node.comparators))
            return f"{left} {ops}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            raise Exception(f"Unsupported node type: {type(node).__name__}")

    def convert_bin_op(self, node: ast.BinOp):

        def convert_binop_operator(operator):
            if isinstance(operator, ast.Add):
                return "+"
            elif isinstance(operator, ast.Sub):
                return "-"
            elif isinstance(operator, ast.Mult):
                return "*"
            elif isinstance(operator, ast.Div):
                return "/"
            # Add more operators as needed
            else:
                raise Exception(f"Unsupported operator: {type(operator).__name__}")
        
        if isinstance(node, ast.BinOp):
            left = self.convert_bin_op(node.left)
            op = convert_binop_operator(node.op)
            right = self.convert_bin_op(node.right)
            return f"{left} {op} {right}"
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            raise Exception(f"Unsupported node type: {type(node).__name__}")

    def convert_unary_op(self, node: ast.UnaryOp):

        def convert_unaryop_operator(operator):
            if isinstance(operator, ast.UAdd):
                return "+"
            elif isinstance(operator, ast.USub):
                return "-"
            elif isinstance(operator, ast.Not):
                return "not "
            elif isinstance(operator, ast.Invert):
                return "~"
            elif isinstance(operator, ast.USub):
                return "-"
            elif isinstance(operator, ast.UAdd):
                return "+"
            elif isinstance(operator, ast.Not):
                return "not "
            elif isinstance(operator, ast.Invert):
                return "~"
            # Add more operators as needed
            else:
                raise Exception(f"Unsupported operator: {type(operator).__name__}")

        if isinstance(node, ast.UnaryOp):
            op = convert_unaryop_operator(node.op)
            operand = self.convert_unary_op(node.operand)
            return f"{op}{operand}"
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return f"Unsupported node type: {type(node).__name__}"

    def convert_lambda(self, node: ast.Lambda):

        def convert_arguments_to_nim(args_node):
            arguments = [arg.arg for arg in args_node.args]
            return " ".join(arguments)

        def convert_body_to_nim(body_node):
            return convert_expr_to_nim(body_node)

        def convert_expr_to_nim(expr_node):
            if isinstance(expr_node, ast.Expr):
                return convert_expr_to_nim(expr_node.value)
            elif isinstance(expr_node, ast.BinOp):
                return f"({convert_expr_to_nim(expr_node.left)} {convert_op_to_nim(expr_node.op)} {convert_expr_to_nim(expr_node.right)})"
            elif isinstance(expr_node, ast.Name):
                return expr_node.id
            elif isinstance(expr_node, ast.Constant):
                return str(expr_node.value)
            else:
                raise ValueError(f"Unsupported expression node: {type(expr_node).__name__}")

        def convert_op_to_nim(op_node):
            if isinstance(op_node, ast.Add):
                return "+"
            elif isinstance(op_node, ast.Sub):
                return "-"
            elif isinstance(op_node, ast.Mult):
                return "*"
            elif isinstance(op_node, ast.Div):
                return "/"
            # Add more operators as needed
            else:
                raise ValueError(f"Unsupported operator node: {type(op_node).__name__}")
                
        if not isinstance(node, ast.Lambda):
            raise ValueError("Input must be an ast.Lambda node")

        args = convert_arguments_to_nim(node.args)
        body = convert_body_to_nim(node.body)

        return f"proc{args}:{body}"

    def convert_if_exp(self, node: ast.IfExp):

        def convert_expr_to_nim(expr_node):
            if isinstance(expr_node, ast.BinOp):
                return f"({convert_expr_to_nim(expr_node.left)} {convert_op_to_nim(expr_node.op)} {convert_expr_to_nim(expr_node.right)})"
            elif isinstance(expr_node, ast.Name):
                return expr_node.id
            elif isinstance(expr_node, ast.Constant):
                return str(expr_node.value)
            elif isinstance(expr_node, ast.IfExp):
                return convert_ifexp_to_nim(expr_node)
            else:
                raise ValueError(f"Unsupported expression node: {type(expr_node).__name__}")

        def convert_op_to_nim(op_node):
            if isinstance(op_node, ast.Add):
                return "+"
            elif isinstance(op_node, ast.Sub):
                return "-"
            elif isinstance(op_node, ast.Mult):
                return "*"
            elif isinstance(op_node, ast.Div):
                return "/"
            # Add more operators as needed
            else:
                raise ValueError(f"Unsupported operator node: {type(op_node).__name__}")

        if not isinstance(node, ast.IfExp):
            raise ValueError("Input must be an ast.IfExp node")

        test = convert_expr_to_nim(node.test)
        body = convert_expr_to_nim(node.body)
        orelse = convert_expr_to_nim(node.orelse)

        return f"if {test}: {body} else: {orelse}"

    def convert_dict(self, node: ast.Dict):
        
        def convert_expr_to_nim(expr_node):
            if isinstance(expr_node, ast.BinOp):
                return f"({convert_expr_to_nim(expr_node.left)} {convert_op_to_nim(expr_node.op)} {convert_expr_to_nim(expr_node.right)})"
            elif isinstance(expr_node, ast.Name):
                return expr_node.id
            elif isinstance(expr_node, ast.Constant):
                return str(expr_node.value)
            elif isinstance(expr_node, ast.Dict):
                return convert_dict_to_nim(expr_node)
            else:
                raise ValueError(f"Unsupported expression node: {type(expr_node).__name__}")

        def convert_op_to_nim(op_node):
            if isinstance(op_node, ast.Add):
                return "+"
            elif isinstance(op_node, ast.Sub):
                return "-"
            elif isinstance(op_node, ast.Mult):
                return "*"
            elif isinstance(op_node, ast.Div):
                return "/"
            # Add more operators as needed
            else:
                raise ValueError(f"Unsupported operator node: {type(op_node).__name__}")

        if not isinstance(node, ast.Dict):
            raise ValueError("Input must be an ast.Dict node")

        keys = []
        values = []

        for key_node, value_node in zip(node.keys, node.values):
            keys.append(convert_expr_to_nim(key_node))
            values.append(convert_expr_to_nim(value_node))

        entries = [f"{key}: {value}" for key, value in zip(keys, values)]

        return f"{{{', '.join(entries)}}}"

    def convert_set(self, node: ast.Set):

        def convert_expr_to_nim(expr_node):
            if isinstance(expr_node, ast.BinOp):
                return f"({convert_expr_to_nim(expr_node.left)} {convert_op_to_nim(expr_node.op)} {convert_expr_to_nim(expr_node.right)})"
            elif isinstance(expr_node, ast.Name):
                return expr_node.id
            elif isinstance(expr_node, ast.Constant):
                return str(expr_node.value)
            elif isinstance(expr_node, ast.Set):
                return convert_set_to_nim(expr_node)
            else:
                raise ValueError(f"Unsupported expression node: {type(expr_node).__name__}")
            
        if not isinstance(node, ast.Set):
            raise ValueError("Input must be an ast.Set node")

        elements = [convert_expr_to_nim(element) for element in node.elts]
        return f"{{ {', '.join(elements)} }}"

    def convert_list_comp(self, node: ast.ListComp):

        def convert_comprehension_to_nim(generator):
            target = convert_expr_to_nim(generator.target)
            iter_expr = convert_expr_to_nim(generator.iter)
            ifs = [f"if {convert_expr_to_nim(iff)}" for iff in generator.ifs]

            return f"for {target} in {iter_expr} {ifs}"

        def convert_expr_to_nim(expr_node):
            if isinstance(expr_node, ast.BinOp):
                return f"({convert_expr_to_nim(expr_node.left)} {convert_op_to_nim(expr_node.op)} {convert_expr_to_nim(expr_node.right)})"
            elif isinstance(expr_node, ast.Name):
                return expr_node.id
            elif isinstance(expr_node, ast.Constant):
                return str(expr_node.value)
            elif isinstance(expr_node, ast.ListComp):
                return convert_listcomp_to_nim(expr_node)
            else:
                raise ValueError(f"Unsupported expression node: {type(expr_node).__name__}")

        def convert_op_to_nim(op_node):
            if isinstance(op_node, ast.Add):
                return "+"
            elif isinstance(op_node, ast.Sub):
                return "-"
            elif isinstance(op_node, ast.Mult):
                return "*"
            elif isinstance(op_node, ast.Div):
                return "/"
            # Add more operators as needed
            else:
                raise ValueError(f"Unsupported operator node: {type(op_node).__name__}")
        
        if not isinstance(node, ast.ListComp):
            raise ValueError("Input must be an ast.ListComp node")

        target = convert_expr_to_nim(node.elt)
        generators = [convert_comprehension_to_nim(generator) for generator in node.generators]

        return f"@[{target} {generators}]"

    def convert_set_comp(self, node: ast.SetComp):
    
        def convert_comprehension_to_nim(generator):
            target = convert_expr_to_nim(generator.target)
            iter_expr = convert_expr_to_nim(generator.iter)
            ifs = [f"if {convert_expr_to_nim(iff)}" for iff in generator.ifs]

            return f"for {target} in {iter_expr} {ifs}"

        def convert_expr_to_nim(expr_node):
            if isinstance(expr_node, ast.BinOp):
                return f"({convert_expr_to_nim(expr_node.left)} {convert_op_to_nim(expr_node.op)} {convert_expr_to_nim(expr_node.right)})"
            elif isinstance(expr_node, ast.Name):
                return expr_node.id
            elif isinstance(expr_node, ast.Constant):
                return str(expr_node.value)
            elif isinstance(expr_node, ast.SetComp):
                return self.convert_set_comp(expr_node)
            else:
                raise ValueError(f"Unsupported expression node: {type(expr_node).__name__}")

        def convert_op_to_nim(op_node):
            if isinstance(op_node, ast.Add):
                return "+"
            elif isinstance(op_node, ast.Sub):
                return "-"
            elif isinstance(op_node, ast.Mult):
                return "*"
            elif isinstance(op_node, ast.Div):
                return "/"
            # Add more operators as needed
            else:
                raise ValueError(f"Unsupported operator node: {type(op_node).__name__}")

        target = convert_expr_to_nim(node.elt)
        generators = [convert_comprehension_to_nim(generator) for generator in node.generators]

        return f"{{ {target} {generators} }}"
    
    def convert_dict_comp(self, node: ast.DictComp):
        target = convert_expr_to_nim(node.elt)
        generators = [convert_comprehension_to_nim(generator) for generator in node.generators]
        return f"{{ {target} {generators} }}"

    def convert_generator_exp(self, node: ast.GeneratorExp):
        elt = convert_expr_to_nim(node.elt)
        generators = [convert_comprehension_to_nim(generator) for generator in node.generators]
        return f"{elt} {generators}"

    def convert_await(self, node: ast.Await):
        #TODO VERY Complex needs work
        pass

    def convert_yield(self, node: ast.Yield):
        #TODO Nim doesn't have direct equivalents for Python generators and the yield statement. 
        # Instead, Nim uses iterators with procedures marked with the iterator pragma.
        pass

    def convert_yield_from(self, node: ast.YieldFrom):

        pass

    def convert_compare(self, node: ast.Compare):
        left = convert_expr_to_nim(node.left)
        comparators = [convert_expr_to_nim(comp) for comp in node.comparators]
        ops = [convert_cmpop_to_nim(op) for op in node.ops]

        comparisons = [f"{left} {op} {comp}" for op, comp in zip(ops, comparators)]
        return " and ".join(comparisons)

    def convert_call(self, node: ast.Call):
        func = convert_expr_to_nim(node.func)
        args = [convert_expr_to_nim(arg) for arg in node.args]
        keywords = [convert_keyword_to_nim(kw) for kw in node.keywords]
        nim_args = ', '.join(args + keywords)
        return f"{func}({nim_args})"

    def convert_formatted_value(self, node: ast.FormattedValue):
        value = convert_expr_to_nim(node.value)
        format_spec = node.format_spec

        if format_spec is not None:
            format_spec_str = convert_expr_to_nim(format_spec)
            return f'"{value, {format_spec_str}}"'
        else:
            return f'"{value}"'

    def convert_joined_str(self, node: ast.JoinedStr):
        parts = [convert_expr_to_nim(value) if isinstance(value, ast.FormattedValue) else str(value.s) for value in node.values]
        return f'"{"".join(parts)}"'

    def convert_num(self, node: ast.Num):
        return str(node.n)

    def convert_str(self, node: ast.Str):
        return f'"{node.s}"'

    def convert_bytes(self, node: ast.Bytes):
        bytes_value = ''.join(f'\\x{byte:02x}' for byte in node.s)
        return f'c"{bytes_value}"'

    def convert_name_constant(self, node: ast.NameConstant):
        if node.value is True:
            return "true"
        elif node.value is False:
            return "false"
        elif node.value is None:
            return "nil"
        else:
            raise ValueError("Unsupported constant value")

    def convert_ellipsis(self, node: ast.Ellipsis):
        return ".."

    def convert_constant(self, node: ast.Constant):
        value = node.value

        if isinstance(value, int):
            return str(value)
        elif isinstance(value, float):
            return str(value)
        elif isinstance(value, str):
            return f'"{value}"'
        elif value is True:
            return "true"
        elif value is False:
            return "false"
        elif value is None:
            return "nil"
        else:
            raise ValueError(f"Unsupported constant value: {value}")

    def convert_named_expr(self, node: ast.NamedExpr):
        target = convert_expr_to_nim(node.target)
        value = convert_expr_to_nim(node.value)

        return f"{target} = {value}"

    def convert_attribute(self, node: ast.Attribute):
        value = convert_expr_to_nim(node.value)
        attr = node.attr

        return f"{value}.{attr}"

    def convert_subscript(self, node: ast.Subscript):
        value = convert_expr_to_nim(node.value)
        slice_expr = convert_slice_to_nim(node.slice)

        return f"{value}[{slice_expr}]"

    def convert_starred(self, node: ast.Starred):
        pass

    def convert_name(self, node: ast.Name):
        return node.id

    def convert_list(self, node: ast.List):
        elements = [convert_expr_to_nim(elem) for elem in node.elts]
        nim_list = f"seq[{', '.join(elements)}]"

        return nim_list

    def convert_tuple(self, node: ast.Tuple):
        elements = [convert_expr_to_nim(elem) for elem in node.elts]
        nim_tuple = f"({', '.join(elements)})"

        return nim_tuple

    def convert_function_def(self, node: ast.FunctionDef):
        function_name = node.name

        # Function parameters
        parameters = [convert_arg_to_nim(arg) for arg in node.args.args]
        parameters_str = ', '.join(parameters)

        # Return type (if specified)
        return_type = ""
        if node.returns:
            return_type = f": {convert_expr_to_nim(node.returns)}"

        # Function body
        body = convert_body_to_nim(node.body)

        # Combine components to form the Nim function
        nim_function = f"proc {function_name}({parameters_str}){return_type} =\n"
        nim_function += body

        return nim_function

    def convert_async_function_def(self, node: ast.AsyncFunctionDef):
        function_name = node.name

        # Async function parameters
        parameters = [convert_arg_to_nim(arg) for arg in node.args.args]
        parameters_str = ', '.join(parameters)

        # Return type (if specified)
        return_type = ""
        if node.returns:
            return_type = f": {convert_expr_to_nim(node.returns)}"

        # Async function body
        body = convert_body_to_nim(node.body)

        # Combine components to form the Nim async function
        asyn = "{.async.}"
        nim_async_function = f"proc {function_name}({parameters_str}){return_type} {asyn} =\n"
        nim_async_function += body

        return nim_async_function

    def convert_class_def(self, node: ast.ClassDef):
        class_name = node.name

        # Base classes
        base_classes = [convert_expr_to_nim(base) for base in node.bases]
        base_classes_str = ', '.join(base_classes)

        # Class attributes and methods
        class_body = convert_classbody_to_nim(node.body)

        # Combine components to form the Nim class
        nim_class = f"type {class_name} = object of {base_classes_str}\n"
        nim_class += class_body

        return nim_class

    def convert_return(self, node: ast.Return):
        return_expr = convert_expr_to_nim(node.value)

        return f"result = {return_expr}"

    def convert_delete(self, node: ast.Delete):
        pass

    def convert_assign(self, node: ast.Assign):
        targets = [convert_expr_to_nim(target) for target in node.targets]
        values = [convert_expr_to_nim(value) for value in node.value.elts]

        nim_assignments = []
        for target, value in zip(targets, values):
            nim_assignment = f"{target} = {value}"
            nim_assignments.append(nim_assignment)

        return "\n".join(nim_assignments)

    def convert_aug_assign(self, node: ast.AugAssign):
        target = convert_expr_to_nim(node.target)
        value = convert_expr_to_nim(node.value)
        op = convert_op_to_nim(node.op)

        nim_assignment = f"{target} {op}= {value}"

        return nim_assignment

    def convert_ann_assign(self, node: ast.AnnAssign):
        target = convert_expr_to_nim(node.target)
        annotation = convert_expr_to_nim(node.annotation)
        value = convert_expr_to_nim(node.value) if node.value else ""

        nim_assignment = f"{target}: {annotation} = {value}"

        return nim_assignment

    def convert_for(self, node: ast.For):
        target = convert_expr_to_nim(node.target)
        iterable = convert_expr_to_nim(node.iter)
        body = convert_body_to_nim(node.body)

        nim_for_loop = f"for {target} in {iterable}:\n"
        nim_for_loop += body

        return nim_for_loop

    def convert_async_for(self, node: ast.AsyncFor):
        target = convert_expr_to_nim(node.target)
        iterable = convert_expr_to_nim(node.iter)
        body = convert_body_to_nim(node.body)

        nim_asyncfor_loop = f"for {target} in {iterable}.itemsAsync():\n"
        nim_asyncfor_loop += body

        return nim_asyncfor_loop

    def convert_while(self, node: ast.While):
        test = convert_expr_to_nim(node.test)
        body = convert_body_to_nim(node.body)

        nim_while_loop = f"while {test}:\n"
        nim_while_loop += body

        return nim_while_loop

    def convert_if(self, node: ast.If):
        test = convert_expr_to_nim(node.test)
        body = convert_body_to_nim(node.body)

        nim_if_statement = f"if {test}:\n"
        nim_if_statement += body

        if node.orelse:
            orelse = convert_orelse_to_nim(node.orelse)
            nim_if_statement += orelse

        return nim_if_statement

    def convert_with(self, node: ast.With):
        context_expr = convert_expr_to_nim(node.context_expr)
        body = convert_body_to_nim(node.body)

        nim_with_statement = f"with {context_expr}:\n"
        nim_with_statement += body

        return nim_with_statement

    def convert_async_with(self, node: ast.AsyncWith):
        context_expr = convert_expr_to_nim(node.context_expr)
        body = convert_body_to_nim(node.body)

        nim_asyncwith_statement = f"await {context_expr}:\n"
        nim_asyncwith_statement += body

        return nim_asyncwith_statement

    def convert_raise(self, node: ast.Raise):
        if node.exc is not None:
            exc_type = convert_expr_to_nim(node.exc)
            nim_raise_statement = f"raise {exc_type}"
        else:
            nim_raise_statement = "raise"

        if node.cause is not None:
            cause = convert_expr_to_nim(node.cause)
            nim_raise_statement += f", {cause}"

        return nim_raise_statement

    def convert_try(self, node: ast.Try):
        body = convert_body_to_nim(node.body)
        excepts = convert_excepts_to_nim(node.handlers)
        orelse = convert_body_to_nim(node.orelse)
        finalbody = convert_body_to_nim(node.finalbody)

        nim_try_statement = f"try:\n{body}"

        if excepts:
            nim_try_statement += f"\n{excepts}"

        if orelse:
            nim_try_statement += f"\nelse:\n{orelse}"

        if finalbody:
            nim_try_statement += f"\nfinally:\n{finalbody}"

        return nim_try_statement

    def convert_try_star(self, node: ast.TryStar):
        # TODO this
        pass

    def convert_assert(self, node: ast.Assert):
        test = convert_expr_to_nim(node.test)
        msg = convert_expr_to_nim(node.msg) if node.msg is not None else ""

        nim_assert_statement = f"assert {test}, {msg}"

        return nim_assert_statement

    def convert_import(self, node: ast.Import):
        nim_import_statements = []

        for alias in node.names:
            module_name = convert_alias_to_nim(alias)
            nim_import_statements.append(f"import {module_name}")

        return "\n".join(nim_import_statements)

    def convert_import_from(self, node: ast.ImportFrom):
        module_name = convert_module_to_nim(node)
        imported_names = convert_imported_names_to_nim(node.names)

        nim_importfrom_statement = f"from {module_name} import {imported_names}"

        return nim_importfrom_statement

    def convert_global(self, node: ast.Global):
        global_vars = ", ".join(node.names)
        nim_comment = f"## Global variables: {global_vars}"

        return nim_comment

    def convert_nonlocal(self, node: ast.Nonlocal):
        nonlocal_vars = ", ".join(node.names)
        nim_comment = f"## Non-local variables captured by closure: {nonlocal_vars}"

        return nim_comment

    def convert_expr(self, node: ast.Expr):
        expr_statement_node = node.value
        

    def convert_pass(self, node: ast.Pass):
        pass

    def convert_break(self, node: ast.Break):
        pass

    def convert_continue(self, node: ast.Continue):
        pass

    def convert_match(self, node: ast.Match):
        pass

    def convert_type_alias(self, node: ast.TypeAlias):
        pass

    def convert_function_definition(self, node:ast.FunctionDef):
        pass

    def convert_module(self, node:ast.Module):
        pass

    def convert_type_ignore(self, node:ast.TypeIgnore):
        pass

    def convert_ext_slice(self, node:ast.ExtSlice):
        pass

    def convert_index(self, node:ast.Index):
        pass

    def convert_aug_load(self, node: ast.AugLoad):
        pass

    def convert_aug_store(self, node: ast.AugStore):
        pass

    def convert_param(self, node: ast.Param):
        pass

    def convert_del(self, node: ast.Del):
        pass

    def convert_load(self, node: ast.Load):
        pass

    def convert_store(self, node: ast.Store):
        pass

    def convert_and(self, node: ast.And):
        pass

    def convert_or(self, node: ast.Or):
        pass

    def convert_add(self, node: ast.Add):
        pass

    def convert_bit_and(self, node: ast.BitAnd):
        pass

    def convert_bit_or(self, node: ast.BitOr):
        pass

    def convert_bit_xor(self, node: ast.BitXor):
        pass

    def convert_div(self, node: ast.Div):
        pass

    def convert_floor_div(self, node: ast.FloorDiv):
        pass

    def convert_l_shift(self, node: ast.LShift):
        pass

    def convert_mod(self, node: ast.Mod):
        pass

    def convert_mult(self, node: ast.Mult):
        pass

    def convert_mat_mult(self, node: ast.MatMult):
        pass

    def convert_pow(self, node: ast.Pow):
        pass

    def convert_r_shift(self, node: ast.RShift):
        pass

    def convert_sub(self, node: ast.Sub):
        pass

    def convert_invert(self, node: ast.Invert):
        pass

    def convert_not(self, node: ast.Not):
        pass

    def convert_u_add(self, node: ast.UAdd):
        pass

    def convert_u_sub(self, node: ast.USub):
        pass

    def convert_eq(self, node: ast.Eq):
        pass

    def convert_gt(self, node: ast.Gt):
        pass

    def convert_gt_e(self, node: ast.GtE):
        pass

    def convert_in(self, node: ast.In):
        pass

    def convert_is(self, node: ast.Is):
        pass

    def convert_is_not(self, node: ast.IsNot):
        pass

    def convert_lt(self, node: ast.Lt):
        pass

    def convert_lt_e(self, node: ast.LtE):
        pass

    def convert_not_eq(self, node: ast.NotEq):
        pass

    def convert_not_in(self, node: ast.NotIn):
        pass

    def convert_match_value(self, node: ast.MatchValue):
        pass

    def convert_match_singleton(self, node: ast.MatchSingleton):
        pass

    def convert_match_sequence(self, node: ast.MatchSequence):
        pass

    def convert_match_star(self, node: ast.MatchStar):
        pass

    def convert_match_mapping(self, node: ast.MatchMapping):
        pass

    def convert_match_class(self, node: ast.MatchClass):
        pass

    def convert_match_as(self, node: ast.MatchAs):
        pass

    def convert_match_or(self, node: ast.MatchOr):
        pass   

    def convert_type_var(self, node: ast.TypeVar):
        pass

    def convert_param_spec(self, node: ast.ParamSpec):
        pass

    def convert_type_var_tuple(self, node: ast.TypeVarTuple):
        pass

    def convert_keyword(self, node: ast.keyword):
        pass

    def convert_alias(self, node: ast.alias):
        pass

    def convert_with_item(self, node: ast.withitem):
        pass

    def convert_keyword(self, node: ast.keyword):
        pass

    def convert_comprehension(self, node: ast.comprehension):
        pass

    def convert_exception_handler(self, node: ast.ExceptHandler):
        pass

    def convert_argument(self, node: ast.arg):
        pass

    def convert_arguments(self, node: ast.arguments):
        pass

    def convert_match_case(self, node: ast.match_case):
        pass 

    def convert_node(self, node: ast.AST) -> str:
        
        self.last_node = self.node
        self.node = node
        
        if issubclass(type(node), ast.mod):
            if isinstance(node, ast.FunctionDef):
                return self.convert_function_definition(node)
            elif isinstance(node, ast.Module):
                return self.convert_module(node)

        elif issubclass(type(node), ast.type_ignore):
            return self.convert_type_ignore(node)

        elif issubclass(type(node), ast.stmt):
            if isinstance(node, ast.FunctionDef):
                return self.convert_function_def(node)
            elif isinstance(node, ast.AsyncFunctionDef):
                return self.convert_async_function_def(node)
            elif isinstance(node, ast.ClassDef):
                return self.convert_class_def(node)
            elif isinstance(node, ast.Return):
                return self.convert_return(node)
            elif isinstance(node, ast.Delete):
                return self.convert_delete(node)
            elif isinstance(node, ast.Assign):
                return self.convert_assign(node)
            elif isinstance(node, ast.AugAssign):
                return self.convert_aug_assign(node)
            elif isinstance(node, ast.AnnAssign):
                return self.convert_ann_assign(node)
            elif isinstance(node, ast.For):
                return self.convert_for(node)
            elif isinstance(node, ast.AsyncFor):
                return self.convert_async_for(node)
            elif isinstance(node, ast.While):
                return self.convert_while(node)
            elif isinstance(node, ast.If):
                return self.convert_if(node)
            elif isinstance(node, ast.With):
                return self.convert_with(node)
            elif isinstance(node, ast.AsyncWith):
                return self.convert_async_with(node)
            elif isinstance(node, ast.Raise):
                return self.convert_raise(node)
            elif isinstance(node, ast.Try):
                return self.convert_try(node)
            elif isinstance(node, ast.TryStar):
                return self.convert_try_star(node)
            elif isinstance(node, ast.Assert):
                return self.convert_assert(node)
            elif isinstance(node, ast.Import):
                return self.convert_import(node)
            elif isinstance(node, ast.ImportFrom):
                return self.convert_import_from(node)
            elif isinstance(node, ast.Global):
                return self.convert_global(node)
            elif isinstance(node, ast.Nonlocal):
                return self.convert_nonlocal(node)
            elif isinstance(node, ast.Expr):
                return self.convert_expr(node)
            elif isinstance(node, ast.Pass):
                return self.convert_pass(node)
            elif isinstance(node, ast.Break):
                return self.convert_break(node)
            elif isinstance(node, ast.Continue):
                return self.convert_continue(node)
            elif isinstance(node, ast.Match):
                return self.convert_match(node)
            elif isinstance(node, ast.TypeAlias):
                return self.convert_type_alias(node)

        elif issubclass(type(node), ast.expr):
            if isinstance(node, ast.BoolOp):
                return self.convert_bool_op(node)
            elif isinstance(node, ast.BinOp):
                return self.convert_bin_op(node)
            elif isinstance(node, ast.UnaryOp):
                return self.convert_unary_op(node)
            elif isinstance(node, ast.Lambda):
                return self.convert_lambda(node)
            elif isinstance(node, ast.IfExp):
                return self.convert_if_exp(node)
            elif isinstance(node, ast.Dict):
                return self.convert_dict(node)
            elif isinstance(node, ast.Set):
                return self.convert_set(node)
            elif isinstance(node, ast.ListComp):
                return self.convert_list_comp(node)
            elif isinstance(node, ast.SetComp):
                return self.convert_set_comp(node)
            elif isinstance(node, ast.DictComp):
                return self.convert_dict_comp(node)
            elif isinstance(node, ast.GeneratorExp):
                return self.convert_generator_exp(node)
            elif isinstance(node, ast.Await):
                return self.convert_await(node)
            elif isinstance(node, ast.Yield):
                return self.convert_yield(node)
            elif isinstance(node, ast.YieldFrom):
                return self.convert_yield_from(node)
            elif isinstance(node, ast.Compare):
                return self.convert_compare(node)
            elif isinstance(node, ast.Call):
                return self.convert_call(node)
            elif isinstance(node, ast.FormattedValue):
                return self.convert_formatted_value(node)
            elif isinstance(node, ast.JoinedStr):
                return self.convert_joined_str(node)
            elif isinstance(node, ast.Num):
                return self.convert_num(node)
            elif isinstance(node, ast.Str):
                return self.convert_str(node)
            elif isinstance(node, ast.Bytes):
                return self.convert_bytes(node)
            elif isinstance(node, ast.NameConstant):
                return self.convert_name_constant(node)
            elif isinstance(node, ast.Ellipsis):
                return self.convert_ellipsis(node)
            elif isinstance(node, ast.Constant):
                return self.convert_constant(node)
            elif isinstance(node, ast.NamedExpr):
                return self.convert_named_expr(node)
            elif isinstance(node, ast.Attribute):
                return self.convert_attribute(node)
            elif isinstance(node, ast.Subscript):
                return self.convert_subscript(node)
            elif isinstance(node, ast.Starred):
                return self.convert_starred(node)
            elif isinstance(node, ast.Name):
                return self.convert_name(node)
            elif isinstance(node, ast.List):
                return self.convert_list(node)
            elif isinstance(node, ast.Tuple):
                return self.convert_tuple(node)

        elif issubclass(type(node), ast.slice):
            if isinstance(node, ast.ExtSlice):
                return self.convert_ext_slice(node)
            if isinstance(node, ast.Index):
                return self.convert_index(node)

        elif issubclass(type(node), ast.expr_context):
            if isinstance(node, ast.AugLoad):
                return self.convert_aug_load(node)
            elif isinstance(node, ast.AugStore):
                return self.convert_aug_store(node)
            elif isinstance(node, ast.Param):
                return self.convert_param(node)
            elif isinstance(node, ast.Del):
                return self.convert_del(node)
            elif isinstance(node, ast.Load):
                return self.convert_load(node)
            elif isinstance(node, ast.Store):
                return self.convert_store(node)
    
        elif issubclass(type(node), ast.boolop):
            if isinstance(node, ast.And):
                return self.convert_and(node)
            if isinstance(node, ast.Or):
                return self.convert_or(node)
    
        elif issubclass(type(node), ast.operator):
            if isinstance(node, ast.Add):
                return self.convert_add(node)
            elif isinstance(node, ast.BitAnd):
                return self.convert_bit_and(node)
            elif isinstance(node, ast.BitOr):
                return self.convert_bit_or(node)
            elif isinstance(node, ast.BitXor):
                return self.convert_bit_xor(node)
            elif isinstance(node, ast.Div):
                return self.convert_div(node)
            elif isinstance(node, ast.FloorDiv):
                return self.convert_floor_div(node)
            elif isinstance(node, ast.LShift):
                return self.convert_l_shift(node)
            elif isinstance(node, ast.Mod):
                return self.convert_mod(node)
            elif isinstance(node, ast.Mult):
                return self.convert_mult(node)
            elif isinstance(node, ast.MatMult):
                return self.convert_mat_mult(node)
            elif isinstance(node, ast.Pow):
                return self.convert_pow(node)
            elif isinstance(node, ast.RShift):
                return self.convert_r_shift(node)
            elif isinstance(node, ast.Sub):
                return self.convert_sub(node)
    
        elif issubclass(type(node), ast.unaryop):
            if isinstance(node, ast.Invert):
                return self.convert_invert(node)
            elif isinstance(node, ast.Not):
                return self.convert_not(node)
            elif isinstance(node, ast.UAdd):
                return self.convert_u_add(node)
            elif isinstance(node, ast.USub):
                return self.convert_u_sub(node)
    
        elif issubclass(type(node), ast.cmpop):
            if isinstance(node, ast.Eq):
                return self.convert_eq(node)
            elif isinstance(node, ast.Gt):
                return self.convert_gt(node)
            elif isinstance(node, ast.GtE):
                return self.convert_gt_e(node)
            elif isinstance(node, ast.In):
                return self.convert_in(node)
            elif isinstance(node, ast.Is):
                return self.convert_is(node)
            elif isinstance(node, ast.IsNot):
                return self.convert_is_not(node)
            elif isinstance(node, ast.Lt):
                return self.convert_lt(node)
            elif isinstance(node, ast.LtE):
                return self.convert_lt_e(node)
            elif isinstance(node, ast.NotEq):
                return self.convert_not_eq(node)
            elif isinstance(node, ast.NotIn):
                return self.convert_not_in(node)
    
        elif issubclass(type(node), ast.comprehension):
            return self.convert_comprehension(node)
    
        elif issubclass(type(node), ast.excepthandler):
            return self.convert_exception_handler(node)
    
        elif issubclass(type(node), ast.arguments):
            return self.convert_arguments(node)
    
        elif isinstance(node, ast.arg):
            return self.convert_argument(node)
    
        elif isinstance(node, ast.keyword):
            return self.convert_keyword(node)
    
        elif isinstance(node, ast.alias):
            return self.convert_alias(node)
    
        elif isinstance(node, ast.withitem):
            return self.convert_with_item(node)
    
        elif isinstance(node, ast.pattern):
            if isinstance(node, ast.MatchValue):
                return self.convert_match_value(node)
            elif isinstance(node, ast.MatchSingleton):
                return self.convert_match_singleton(node)
            elif isinstance(node, ast.MatchSequence):
                return self.convert_match_sequence(node)
            elif isinstance(node, ast.MatchStar):
                return self.convert_match_star(node)
            elif isinstance(node, ast.MatchMapping):
                return self.convert_match_mapping(node)
            elif isinstance(node, ast.MatchClass):
                return self.convert_match_class(node)
            elif isinstance(node, ast.MatchAs):
                return self.convert_match_as(node)
            elif isinstance(node, ast.MatchOr):
                return self.convert_match_or(node)
    
        elif isinstance(node, ast.match_case):
            return self.convert_match_case(node)
    
        elif isinstance(node, ast.type_param):
            if isinstance(node, ast.TypeVar):
                return self.convert_type_var(node)
            elif isinstance(node, ast.ParamSpec):
                return self.convert_param_spec(node)
            elif isinstance(node, ast.TypeVarTuple):
                return self.convert_type_var_tuple(node)
    
    def convert_file(self, filepath:str):
        with open(filepath, 'r') as f:
            source = f.read()
        tree = ast.parse(source, type_comments=True)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        for function in functions:
            print(self.convert_function_def(function))
            
        

def test():
    cc = CodeConverter()
    cc.convert_file(__file__)

test()