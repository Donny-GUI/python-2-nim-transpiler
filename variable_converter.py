import ast


class VariableInfo(object):
    def __init__(self, name:str=None, types:list[str]=[], scope:ast.AST=None, count=1, node_indexes: list[int]=[None]) -> None:
        self.name = name
        self.types = types
        self.scope = scope
        self.count = count
        self.node_indexes = node_indexes
        self.returned = False
        self.mutable = True
        self.values = []
        
def analyze_variables(source_code):
    tree = ast.parse(source_code)
    
    variables_info = {}

    def visit(node, current_scope):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variable_name = target.id
                    variables_info[variable_name] = evaluate_expression(node.value, current_scope)

        elif isinstance(node, ast.FunctionDef):
            # Create a new scope for function definition
            new_scope = current_scope.copy()
            for arg in node.args.args:
                new_scope[arg.arg] = None  # Initialize function arguments to None
            for stmt in node.body:
                visit(stmt, new_scope)

        elif isinstance(node, ast.For):
            # Create a new scope for the for loop
            new_scope = current_scope.copy()
            new_scope[node.target.id] = None  # Initialize loop variable to None
            for stmt in node.body:
                visit(stmt, new_scope)

        elif isinstance(node, ast.While):
            # Create a new scope for the while loop
            new_scope = current_scope.copy()
            for stmt in node.body:
                visit(stmt, new_scope)

        elif isinstance(node, ast.If) or isinstance(node, ast.With):
            # Create a new scope for the if statement or with statement
            new_scope = current_scope.copy()
            for stmt in node.body:
                visit(stmt, new_scope)
            for stmt in node.orelse:
                visit(stmt, new_scope)

        else:
            for child_node in ast.iter_child_nodes(node):
                visit(child_node, current_scope)

    def evaluate_expression(expr, scope):
        if isinstance(expr, ast.Name):
            return variables_info.get(expr.id, None)
        elif isinstance(expr, ast.BinOp):
            left_value = evaluate_expression(expr.left, scope)
            right_value = evaluate_expression(expr.right, scope)
            if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                if isinstance(expr.op, ast.Add):
                    return left_value + right_value
                elif isinstance(expr.op, ast.Sub):
                    return left_value - right_value
                elif isinstance(expr.op, ast.Mult):
                    return left_value * right_value
                elif isinstance(expr.op, ast.Div):
                    return left_value / right_value
            elif isinstance(left_value, str) and isinstance(right_value, str) and isinstance(expr.op, ast.Add):
                return left_value + right_value
            elif isinstance(left_value, bool) and isinstance(right_value, bool) and isinstance(expr.op, ast.And):
                return left_value and right_value
            elif isinstance(left_value, bool) and isinstance(right_value, bool) and isinstance(expr.op, ast.Or):
                return left_value or right_value
        elif isinstance(expr, ast.Num):
            return expr.n
        elif isinstance(expr, ast.Str):
            return expr.s
        elif isinstance(expr, ast.List):
            return [evaluate_expression(e, scope) for e in expr.elts]
        elif isinstance(expr, ast.Dict):
            return {evaluate_expression(k, scope): evaluate_expression(v, scope) for k, v in zip(expr.keys, expr.values)}
        elif isinstance(expr, ast.NameConstant):
            return expr.value
        elif isinstance(expr, ast.BoolOp):
            if isinstance(expr.op, ast.And):
                return all(evaluate_expression(e, scope) for e in expr.values)
            elif isinstance(expr.op, ast.Or):
                return any(evaluate_expression(e, scope) for e in expr.values)
        # Add more cases as needed for other expression types

    visit(tree, {})

    return variables_info

def find_nodes_with_name(module: ast.Module, target_name:ast.Name):
    result_nodes = []

    def visit(node):
        if isinstance(node, ast.Name) and node.id == target_name.id:
            result_nodes.append(node)
        for child_node in ast.iter_child_nodes(node):
            visit(child_node)

    visit(module)

    return result_nodes


class VariableAnalyzer(object):
    NameSuperNodes = (
        ast.For, ast.With, 
        ast.Global, ast.Nonlocal, 
        ast.NameConstant, ast.ExceptHandler, 
        ast.arg, ast.FunctionDef, 
        ast.AsyncFunctionDef
    )
    def __init__(self) -> None:
        self.node = None
        self.mutable = False
        self.types = []
        self.equal_to = []
        self.variables_set_to = []
        self.nodes_that_contain = []

    def analyze_variable_in_module(self, module:ast.Module, variable:ast.Name):
        all_nodes = find_nodes_with_name(module, variable)
        all_values = []

        for node in all_nodes:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                value = node.value
                all_values.append(value)
            elif isinstance(node, ast.Assign) and len(node.targets) != 1:
                myindex = 0
                for index, target in enumerate(node.targets):
                    if target == variable:
                        myindex = index
                        break
                if isinstance(node.value, ast.List):
                    all_values.append(node.value.elts[myindex])
                elif isinstance(node.value, ast.Tuple):
                    all_values.append(node.value.elts[myindex])
                elif isinstance(node.value, ast.Str):
                    all_values.append(node.value.value[myindex])
                elif isinstance(node.value, ast.ListComp):
                    pass

    def analyze_source_code(self, source):
        variables = analyze_variables(source)
        from pprint import pprint
        pprint(variables)


    def analyze_variable_in_function(self, function: ast.FunctionDef, variable: ast.Name):
        self.node = variable

        equal_to_types  = []  # types that this variable is set equal to
        equal_to_values = []  # values that this variable is set equal to
        equal_to_calls  = []  # function calls that this variable is set equal to
        values_equal_to = []  # variables that this variable is set equal to
        inside_nodes    = []  # nodes that this variable is inside of

        nodes   = function.body 
        name    = variable.id
        context = variable.ctx

        has_variable = False 
        mulit_use    = False

        # iterate through the body nodes
        for node in nodes:
            has_variable = False
            multi_use    = False
            # get the base type of node
            node_type = type(node)
            
            # walk the node subnodes
            for subnode in ast.walk(node):
                # check to see if the node is a variable name
                # and check to see if it is the variable, and if it has been used before
                if isinstance(subnode, ast.Name) and subnode.id == name:
                    if has_variable == True:
                        mulit_use = True 
                    has_variable = True
                    continue
            
            if has_variable == True:
                inside_nodes.append(node)
            
            if isinstance(node, ast.Assign):
                pass
