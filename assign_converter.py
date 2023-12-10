import ast
import astor


class AssignConverter:
    """
    Converts Python assignment statements to Nim syntax.

    Attributes:
    - assign_node (Optional[ast.Assign]): The AST node representing the assignment.
    - targets (List[str]): The list of target variables in the assignment.
    - value (Optional[str]): The value being assigned.
    """
    def __init__(self):
        self.assign_node = None
        self.targets = []
        self.value = None

    def convert(self, node: ast.Assign):
        """
        Analyze the ast.Assign node and extract information.

        Parameters:
        - node (ast.Assign): The AST node representing the assignment.
        """
        self.assign_node = node
        self.targets = [target.id for target in self.assign_node.targets if isinstance(target, ast.Name)]
        self.value = astor.to_source(self.assign_node.value).strip()
        
    def get(self):
        """
        Convert the ast.Assign node to Nim syntax.

        Returns:
        - str: Nim syntax representation of the assignment.
        """
        nim_code = f"{', '.join(self.targets)} = {self.value}"
        return nim_code
    