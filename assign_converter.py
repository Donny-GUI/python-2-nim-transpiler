import ast
import astor


class AssignConverter2:

    def convert_assign(node: ast.Assign) -> str:
        targets = [ast.unparse(target) for target in node.targets]
        value = ast.unparse(node.value)
        return f'{", ".join(targets)} = {value}'

    def convert_aug_assign(node: ast.AugAssign) -> str:
        target = ast.unparse(node.target)
        op = node.op.__class__.__name__
        value = ast.unparse(node.value)
        
        # Mapping of Python augmented assignment operators to Nim equivalents
        nim_operators = {
            'Add': '+=',
            'Sub': '-=',
            'Mult': '*=',
            'Div': '/=',
            'Mod': '%=',
            'BitAnd': '&=',
            'BitOr': '|=',
            'BitXor': '^=',
            'LShift': '<<=',
            'RShift': '>>=',
            'FloorDiv': '//=',
            'Pow': '**=',
        }
        
        nim_operator = nim_operators.get(op, op)
        
        return f'{target} {nim_operator} {value}'






class AssignConverter:
    def __init__(self):
        self.assign_node = None
        self.targets = []
        self.value = None

    def convert(self, node: ast.Assign):
        """
        Analyze the ast.Assign node and extract information.
        """
        self.assign_node = node
        self.targets = [target.id for target in self.assign_node.targets if isinstance(target, ast.Name)]
        self.value = astor.to_source(self.assign_node.value).strip()
        
    def get(self):
        """
        Convert the ast.Assign node to Nim syntax.
        """
        nim_code = f"{', '.join(self.targets)} = {self.value}"
        return nim_code
    