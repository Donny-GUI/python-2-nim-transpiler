import std/strutils
import tables

    



##########################################
#  Functions  
##########################################

proc name(anyclass: any = nil): string = 
  return anyclass.__name__

proc attributes(anyclass: any = nil): seq[string] = 
  return [attr for attr in vars(anyclass) if not callable(getattr(anyclass, attr)) and (not attr.startsWith("__"))]

proc properties(anyclass: any = nil): seq[string] = 
  proc make_instance(anyclass, args=0):
    if args != 0:
      values = nil * args
      try:
        instance = anyclass(*values)
      except:
        instance = make_instance(anyclass, args + 1)
      finally:
        return instance
    else:
      try:
        instance = anyclass()
      except:
        instance = make_instance(anyclass, args + 1)
      finally:
        return instance
  my_instance = make_instance(anyclass)
  all_attributes = dir(my_instance)
  return [attr for attr in all_attributes if not callable(getattr(my_instance, attr)) and (not attr.startsWith("__"))]

proc makeInstance(anyclass: nil = nil, args: nil = 0): nil = 
  if args != 0:
    values = nil * args
    try:
      instance = anyclass(*values)
    except:
      instance = make_instance(anyclass, args + 1)
    finally:
      return instance
  else:
    try:
      instance = anyclass()
    except:
      instance = make_instance(anyclass, args + 1)
    finally:
      return instance

proc convertSubscriptToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.Subscript):
    raise ValueError("Input must be an ast.Subscript node")
  value = convert_expr_to_nim(node.value)
  slice_expr = convert_slice_to_nim(node.slice)
  return fmt"{value}[{slice_expr}]"

proc convertSliceToNim(slice_node: nil = nil): nil = 
  if isinstance(slice_node, ast.Index):
    return convert_expr_to_nim(slice_node.value)
  elif isinstance(slice_node, ast.Slice):
    lower = convert_expr_to_nim(slice_node.downcase) if slice_node.downcase else ""
    upper = convert_expr_to_nim(slice_node.upcase) if slice_node.upcase else ""
    step = convert_expr_to_nim(slice_node.step) if slice_node.step else ""
    return fmt"{lower}:{upper}:{step}"
  else:
    discard

proc convertKeywordToNim(keyword: nil = nil): nil = 
  return fmt"{keyword.arg} = {convert_expr_to_nim(keyword.value)}"

proc convertCmpopToNim(cmpop_node: nil = nil): nil = 
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
  else:
    raise ValueError(fmt"Unsupported comparison operator node: {type(cmpop_node).__name__}")

proc convertSetcompToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.SetComp):
    raise ValueError("Input must be an ast.SetComp node")
  target = convert_expr_to_nim(node.elt)
  generators = [convert_comprehension_to_nim(generator) for generator in node.generators]
  return fmt"{{ {target} {generators} }}"

proc convertComprehensionToNim(generator: nil = nil): nil = 
  target = convert_expr_to_nim(generator.target)
  iter_expr = convert_expr_to_nim(generator.iter)
  ifs = [fmt"if {convert_expr_to_nim(iff)}" for iff in generator.ifs]
  return fmt"for {target} in {iter_expr} {ifs}"

proc convertJoinedstrToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.JoinedStr):
    raise ValueError("Input must be an ast.JoinedStr node")
  parts = [convert_expr_to_nim(value) if isinstance(value, ast.FormattedValue) else string(value.s) for value in node.values]
  return fmt""{"".join(parts)}""

proc convertFormattedvalueToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.FormattedValue):
    raise ValueError("Input must be an ast.FormattedValue node")
  value = convert_expr_to_nim(node.value)
  format_spec = node.format_spec
  if format_spec isnot nil:
    format_spec_str = convert_expr_to_nim(format_spec)
    return fmt""{(value, {format_spec_str})}""
  else:
    return fmt""{value}""

proc convertNamedexprToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.NamedExpr):
    raise ValueError("Input must be an ast.NamedExpr node")
  target = convert_expr_to_nim(node.target)
  value = convert_expr_to_nim(node.value)
  return fmt"{target} = {value}"

proc convertAttributeToNim(node: nil = nil): nil = 
  attribute_name = convert_expr_to_nim(node.value)
  attribute_value = convert_expr_to_nim(node.value)
  nim_attribute = fmt"{attribute_name} = {attribute_value}"
  return nim_attribute

proc convertStarredToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.Starred):
    raise ValueError("Input must be an ast.Starred node")
  value = convert_expr_to_nim(node.value)
  return fmt"@{value}"

proc convertListToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.List):
    raise ValueError("Input must be an ast.List node")
  elements = [convert_expr_to_nim(elem) for elem in node.elts]
  nim_@[] = fmt"seq[{", ".join(elements)}]"
  return nim_@[]

proc convertTupleToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.Tuple):
    raise ValueError("Input must be an ast.Tuple node")
  elements = [convert_expr_to_nim(elem) for elem in node.elts]
  nim_tuple = fmt"({", ".join(elements)})"
  return nim_tuple

proc convertAsyncfunctiondefToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.AsyncFunctionDef):
    raise ValueError("Input must be an ast.AsyncFunctionDef node")
  function_name = node.name
  parameters = [convert_arg_to_nim(arg) for arg in node.args.args]
  var parameters_str: string = ", ".join(parameters)
  var return_type: string = ""
  if node.returns:
    return_type = fmt": {convert_expr_to_nim(node.returns)}"
  body = convert_body_to_nim(node.body)
  var asy: string = "{.async.}"
  nim_async_function = fmt"proc {function_name}({parameters_str}){return_type} {asy} =\n"
  nim_async_function += body
  return nim_async_function

proc convertClassdefToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.ClassDef):
    raise ValueError("Input must be an ast.ClassDef node")
  class_name = node.name
  base_classes = [convert_expr_to_nim(base) for base in node.bases]
  var base_classes_str: string = ", ".join(base_classes)
  class_body = convert_classbody_to_nim(node.body)
  nim_class = fmt"type {class_name} = object of {base_classes_str}\n"
  nim_class += class_body
  return nim_class

proc convertClassbodyToNim(body_nodes: nil = nil): nil = 
  return "\n".join([convert_classstmt_to_nim(stmt) for stmt in body_nodes])

proc convertClassstmtToNim(stmt_node: nil = nil): nil = 
  if isinstance(stmt_node, ast.FunctionDef):
    return convert_method_to_nim(stmt_node)
  elif isinstance(stmt_node, ast.AsyncFunctionDef):
    return convert_method_to_nim(stmt_node, is_async=True)
  elif isinstance(stmt_node, ast.Assign):
    return convert_attribute_to_nim(stmt_node)
  else:
    raise ValueError(fmt"Unsupported class statement node: {type(stmt_node).__name__}")

proc convertMethodToNim(node: nil = nil, is_async: nil = false): nil = 
  method_name = node.name
  parameters = [convert_arg_to_nim(arg) for arg in node.args.args]
  var parameters_str: string = ", ".join(parameters)
  var return_type: string = ""
  if node.returns:
    return_type = fmt": {convert_expr_to_nim(node.returns)}"
  body = convert_body_to_nim(node.body)
  var method_prefix: string = "proc" if not is_async else "proc {.async.}"
  nim_method = fmt"{method_prefix} {method_name}({parameters_str}){return_type} =\n"
  nim_method += body
  return nim_method

proc convertAttributeToNim(node: nil = nil): nil = 
  attribute_name = convert_expr_to_nim(node.value)
  attribute_value = convert_expr_to_nim(node.value)
  nim_attribute = fmt"{attribute_name} = {attribute_value}"
  return nim_attribute

proc convertFunctiondefToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.FunctionDef):
    raise ValueError("Input must be an ast.FunctionDef node")
  function_name = node.name
  parameters = [convert_arg_to_nim(arg) for arg in node.args.args]
  var parameters_str: string = ", ".join(parameters)
  var return_type: string = ""
  if node.returns:
    return_type = fmt": {convert_expr_to_nim(node.returns)}"
  body = convert_body_to_nim(node.body)
  nim_function = fmt"proc {function_name}({parameters_str}){return_type} =\n"
  nim_function += body
  return nim_function

proc convertArgToNim(arg_node: nil = nil): nil = 
  if isinstance(arg_node, ast.arg):
    return arg_node.arg
  else:
    raise ValueError("Unsupported argument node")

proc convertBodyToNim(body_nodes: nil = nil): nil = 
  return "\n".join([convert_stmt_to_nim(stmt) for stmt in body_nodes])

proc convertAsyncforToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.AsyncFor):
    raise ValueError("Input must be an ast.AsyncFor node")
  target = convert_expr_to_nim(node.target)
  iterable = convert_expr_to_nim(node.iter)
  body = convert_body_to_nim(node.body)
  nim_asyncfor_loop = fmt"for {target} in {iterable}.itemsAsync():\n"
  nim_asyncfor_loop += body
  return nim_asyncfor_loop

proc convertStmtToNim(stmt_node: nil = nil): nil = 
  if isinstance(stmt_node, ast.Expr):
    return convert_expr_to_nim(stmt_node.value)
  elif isinstance(stmt_node, ast.Return):
    x = fmt"result = {convert_expr_to_nim(stmt_node.value)}"
    return x
  elif isinstance(stmt_node, ast.Assign):
    return convert_assign_to_nim(stmt_node)
  elif isinstance(stmt_node, ast.FunctionDef):
    return convert_functiondef_to_nim(stmt_node)
  elif isinstance(stmt_node, ast.If):
    return convert_if_to_nim(stmt_node)
  elif isinstance(stmt_node, ast.Try):
    return convert_try_to_nim(stmt_node)
  elif stmt_node.value == nil:
    return "nil"
  else:
    raise ValueError(fmt"Unsupported statement node: {type(stmt_node).__name__}")

proc convertAssignToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.Assign):
    raise ValueError("Input must be an ast.Assign node")
  if isinstance(node.value, ast.Constant):
    return convert_constant_to_nim(node)
  var targets: seq = @[]
  for x in node.targets:
    if isinstance(x, ast.Constant):
      targets.add(convert_constant_to_nim(x))
    else:
      targets.add(convert_expr_to_nim(x))
  var values: seq = @[]
  if isinstance(node.value, ast.IfExp):
    return
  if isinstance(node.value, ast.BinOp):
    return string(node.value)
  for value in node.value.elts:
    try:
      values.add(convert_expr_to_nim(value))
    except AttributeError:
      if isinstance(value, ast.Constant):
        values.add(convert_constant_to_nim(value))
  var nim_assignments: seq = @[]
  for target, value in zip(targets, values):
    nim_assignment = fmt"{target} = {value}"
    nim_assignments.add(nim_assignment)
  return "\n".join(nim_assignments)

proc convertAugassignToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.AugAssign):
    raise ValueError("Input must be an ast.AugAssign node")
  target = convert_expr_to_nim(node.target)
  value = convert_expr_to_nim(node.value)
  op = convert_op_to_nim(node.op)
  nim_assignment = fmt"{target} {op}= {value}"
  return nim_assignment

proc convertAnnassignToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.AnnAssign):
    raise ValueError("Input must be an ast.AnnAssign node")
  target = convert_expr_to_nim(node.target)
  annotation = convert_expr_to_nim(node.annotation)
  value = convert_expr_to_nim(node.value) if node.value else ""
  nim_assignment = fmt"{target}: {annotation} = {value}"
  return nim_assignment

proc convertForToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.For):
    raise ValueError("Input must be an ast.For node")
  target = convert_expr_to_nim(node.target)
  iterable = convert_expr_to_nim(node.iter)
  body = convert_body_to_nim(node.body)
  nim_for_loop = fmt"for {target} in {iterable}:\n"
  nim_for_loop += body
  return nim_for_loop

proc convertWhileToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.While):
    raise ValueError("Input must be an ast.While node")
  test = convert_expr_to_nim(node.test)
  body = convert_body_to_nim(node.body)
  nim_while_loop = fmt"while {test}:\n"
  nim_while_loop += body
  return nim_while_loop

proc convertCompareToNim(compare_node: nil = nil): nil = 
  left = convert_expr_to_nim(compare_node.left)
  right = convert_expr_to_nim(compare_node.comparators[0])
  op = convert_cmpop_to_nim(compare_node.ops[0])
  return fmt"({left} {op} {right})"

proc convertCmpopToNim(cmpop_node: nil = nil): nil = 
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
  else:
    raise ValueError(fmt"Unsupported comparison operator node: {type(cmpop_node).__name__}")

proc convertIfToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.If):
    raise ValueError("Input must be an ast.If node")
  test = convert_expr_to_nim(node.test)
  body = convert_body_to_nim(node.body)
  nim_if_statement = fmt"if {test}:\n"
  nim_if_statement += body
  if node.orelse:
    orelse = convert_orelse_to_nim(node.orelse)
    nim_if_statement += orelse
  return nim_if_statement

proc convertOrelseToNim(orelse_nodes: nil = nil): nil = 
  if not orelse_nodes:
    return ""
  if isinstance(orelse_nodes[0], ast.If):
    return convert_if_to_nim(orelse_nodes[0])
  else:
    return "else:\n" + convert_body_to_nim(orelse_nodes)

proc convertWithToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.With):
    raise ValueError("Input must be an ast.With node")
  context_expr = convert_expr_to_nim(node.context_expr)
  body = convert_body_to_nim(node.body)
  nim_with_statement = fmt"with {context_expr}:\n"
  nim_with_statement += body
  return nim_with_statement

proc convertAsyncwithToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.AsyncWith):
    raise ValueError("Input must be an ast.AsyncWith node")
  context_expr = convert_expr_to_nim(node.context_expr)
  body = convert_body_to_nim(node.body)
  nim_asyncwith_statement = fmt"await {context_expr}:\n"
  nim_asyncwith_statement += body
  return nim_asyncwith_statement

proc convertRaiseToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.Raise):
    raise ValueError("Input must be an ast.Raise node")
  if node.exc isnot nil:
    exc_type = convert_expr_to_nim(node.exc)
    nim_raise_statement = fmt"raise {exc_type}"
  else:
    var nim_raise_statement: string = "raise"
  if node.cause isnot nil:
    cause = convert_expr_to_nim(node.cause)
    nim_raise_statement += fmt", {cause}"
  return nim_raise_statement

proc convertTryToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.Try):
    raise ValueError("Input must be an ast.Try node")
  body = convert_body_to_nim(node.body)
  excepts = convert_excepts_to_nim(node.handlers)
  orelse = convert_body_to_nim(node.orelse)
  finalbody = convert_body_to_nim(node.finalbody)
  nim_try_statement = fmt"try:\n{body}"
  if excepts:
    nim_try_statement += fmt"\n{excepts}"
  if orelse:
    nim_try_statement += fmt"\nelse:\n{orelse}"
  if finalbody:
    nim_try_statement += fmt"\nfinally:\n{finalbody}"
  return nim_try_statement

proc convertExceptsToNim(handlers: nil = nil): nil = 
  if not handlers:
    return ""
  var nim_excepts: seq = @[]
  for handler in handlers:
    except_type = convert_expr_to_nim(handler.type)
    except_body = convert_body_to_nim(handler.body)
    nim_except = fmt"except {except_type}:\n{except_body}"
    nim_excepts.add(nim_except)
  return "\n".join(nim_excepts)

proc convertAssertToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.Assert):
    raise ValueError("Input must be an ast.Assert node")
  test = convert_expr_to_nim(node.test)
  msg = convert_expr_to_nim(node.msg) if node.msg is not nil else ""
  nim_assert_statement = fmt"assert {test}, {msg}"
  return nim_assert_statement

proc convertImportToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.Import):
    raise ValueError("Input must be an ast.Import node")
  var nim_import_statements: seq = @[]
  for alias in node.names:
    module_name = convert_alias_to_nim(alias)
    nim_import_statements.add(fmt"import {module_name}")
  return "\n".join(nim_import_statements)

proc convertAliasToNim(alias: nil = nil): nil = 
  if alias.asname isnot nil:
    return fmt"{alias.name} as {alias.asname}"
  else:
    return alias.name

proc convertTargetToNim(node: nil = nil): nil = 
  if isinstance(node, ast.Name):
    return node.id
  elif isinstance(node, ast.Call):
    return convert_call_to_nim(node)
  else:
    raise ValueError(fmt"Unsupported target node: {type(node).__name__}")

proc convertAstNodeToNim(node: nil = nil): nil = 
  if isinstance(node, ast.BinOp):
    left = convert_ast_node_to_nim(node.left)
    right = convert_ast_node_to_nim(node.right)
    op = convert_op_to_nim(node.op)
    return fmt"({left} {op} {right})"
  elif isinstance(node, ast.Name):
    return node.id
  elif isinstance(node, ast.Constant):
    return string(node.value)
  elif isinstance(node, ast.Call):
    return convert_call_to_nim(node)
  elif isinstance(node, ast.Attribute):
    return convert_attribute_to_nim(node)
  else:
    raise ValueError(fmt"Unsupported expression node: {type(node).__name__}")

proc convertListcompToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.ListComp):
    raise ValueError("Input must be an ast.ListComp node")
  target = node.elt
  generators = node.generators
  var nim_code: string = "var result: seq["
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

proc convertImportfromToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.ImportFrom):
    raise ValueError("Input must be an ast.ImportFrom node")
  module_name = convert_module_to_nim(node)
  imported_names = convert_imported_names_to_nim(node.names)
  nim_importfrom_statement = fmt"from {module_name} import {imported_names}"
  return nim_importfrom_statement

proc convertModuleToNim(node: nil = nil): nil = 
  module_name = node.module
  if node.level > 0:
    var module_name: string = "." * node.level + module_name
  return module_name

proc convertImportedNamesToNim(names: nil = nil): nil = 
  var nim_imported_names: seq = @[]
  for alias in names:
    nim_imported_names.add(convert_alias_to_nim(alias))
  return ", ".join(nim_imported_names)

proc convertLambdaToNim(node: nil = nil): nil = 
  var parameters: string = ", ".join((param.arg for param in node.args.args))
  nim_proc = fmt"proc ({parameters}): "
  body = convert_expr_to_nim(node.body)
  nim_proc += fmt"{body}"
  return nim_proc

proc convertConstantToNim(node: nil = nil): nil = 
  if node.value == nil:
    return "nil"
  value = node.value
  nim_literal = convert_value_to_nim_literal(value)
  return nim_literal

proc convertValueToNimLiteral(value: nil = nil): nil = 
  lit = ast.unparse(value)
  if isinstance(value, str):
    return fmt""{value}""
  elif isinstance(value, bool):
    return string(value).downcase()
  elif isinstance(value, (int, float)):
    return string(value)
  elif value.value == nil:
    return "nil"
  elif value is nil:
    return "nil"
  elif value.value == 0:
    return "0"
  elif lit == "" or value.value == "":
    return ""
  else:
    raise ValueError(fmt"Unsupported constant value: {value}")

proc convertGeneratorexpToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.GeneratorExp):
    raise ValueError("Input must be an ast.GeneratorExp node")
  target = node.elt
  generators = node.generators
  var nim_code: string = "iterator "
  nim_code += convert_target_to_nim(target)
  nim_code += fmt"():\n"
  for generator in generators:
    nim_code += "  for "
    nim_code += convert_target_to_nim(generator.target)
    nim_code += " in "
    nim_code += convert_ast_node_to_nim(generator.iter)
    nim_code += ":\n"
  nim_code += "  yield "
  nim_code += convert_ast_node_to_nim(target)
  return nim_code

proc convertExprToNim(expr_node: nil = nil): nil = 
  if isinstance(expr_node, ast.BinOp):
    return fmt"({convert_expr_to_nim(expr_node.left)} {convert_op_to_nim(expr_node.op)} {convert_expr_to_nim(expr_node.right)})"
  elif isinstance(expr_node, ast.Name):
    return expr_node.id
  elif isinstance(expr_node, ast.Constant):
    return string(expr_node.value)
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
    return convert_@[]_to_nim(expr_node)
  elif isinstance(expr_node, ast.Tuple):
    return convert_tuple_to_nim(expr_node)
  elif isinstance(expr_node, ast.Compare):
    return convert_compare_to_nim(expr_node)
  elif isinstance(expr_node, ast.Lambda):
    return convert_proc_to_nim(expr_node)
  elif isinstance(expr_node, ast.ListComp):
    return convert_@[]comp_to_nim(expr_node)
  elif isinstance(expr_node, ast.GeneratorExp):
    return convert_generatorexp_to_nim(expr_node)
  else:
    raise ValueError(fmt"Unsupported expression node: {type(expr_node).__name__}")

proc convertCallToNim(node: nil = nil): nil = 
  if not isinstance(node, ast.Call):
    raise ValueError("Input must be an ast.Call node")
  func = convert_expr_to_nim(node.func)
  args = [convert_expr_to_nim(arg) for arg in node.args]
  keywords = [convert_keyword_to_nim(kw) for kw in node.keywords]
  var nim_args: string = ", ".join(args + keywords)
  return fmt"{func}({nim_args})"

proc convertOpToNim(op_node: nil = nil): nil = 
  if isinstance(op_node, ast.Add):
    return "+"
  elif isinstance(op_node, ast.Sub):
    return "-"
  elif isinstance(op_node, ast.Mult):
    return "*"
  elif isinstance(op_node, ast.Div):
    return "/"
  else:
    raise ValueError(fmt"Unsupported operator node: {type(op_node).__name__}")

proc test(): nil = 
  cc = CodeConverter()
  cc.convert_file(__file__)
