import ast
from type_converter import TypeConverter
from class_analyzer import ClassAnalyzer
from method_converter import MethodConverter
from util import get_python_nodes


class ClassConverter(object):
    """
    Converts Python class information to Nim code.

    Attributes:
    - class_properties (tuple): Tuple containing class property names.
    - classes (List[str]): List of class names.
    - procs (Dict): Dictionary containing procedural information.
    - init_procs (Dict): Dictionary containing initialization procedural information.
    - type_definitions (Dict[str, str]): Dictionary containing type definitions for classes.
    - method_signatures (Dict[str, Dict[str, str]]): Dictionary containing method signatures for classes.
    - method_bodies (Dict[str, Dict[str, str]]): Dictionary containing method bodies for classes.
    - init_methods (Dict[str, str]): Dictionary containing initialization methods for classes.
    - method_names (Dict[str, List[str]]): Dictionary containing lists of method names for classes.
    """
    class_properties = "name", "type definition", "initializer method", "methods"
    
    def __init__(self) -> None:
        """
        Initialize ClassConverter.
        """
        self.classes = []
        self.procs = {}
        self.init_procs = {}
        self.type_definitions = {}
        self.method_signatures = {}
        self.method_bodies = {}
        self.init_methods = {}
        self.method_names = {}

    def add_class(self, analyzer: ClassAnalyzer) -> None:
        """
        Add information about a class to the converter.

        Parameters:
        - analyzer (ClassAnalyzer): The ClassAnalyzer instance containing class information.
        """
        type_definiton_code = "type\n  "
        data = analyzer.data()

        self.classes.append(data["name"])

        # type definition creation
        type_definiton_code+=str(data["name"]) + " = object\n"
        propnames = []

        for prop in data["initializer"]["properties"]:
            
            if prop["name"] not in propnames:
                val = prop["type"]
                nimtype = TypeConverter.convert_type_by_string_name(val)
                type_definiton_code+="    " + prop["name"] + ": " + nimtype + "\n"
                propnames.append(prop["name"])

        self.type_definitions[data["name"]] = type_definiton_code
        
        # Get the method signatures
        self.method_bodies[data["name"]] = {}
        self.method_signatures[data["name"]] = {}
        self.method_bodies[data["name"]] = {}
        self.method_names[data["name"]] = []

        for meth in [node for node in analyzer.node.body if isinstance(node, ast.FunctionDef)]:
            methconverter = MethodConverter()
            # initalization method signature creation
            if meth.name.startswith("__init") and meth.name.endswith("__"):
                self.init_methods[analyzer.node.name] = methconverter.convert_initializer_signature(meth, analyzer.node)
                continue

            # get the method signature
            self.method_signatures[analyzer.node.name][meth.name] = methconverter.convert_method_signature(meth, analyzer.node)
            # get the method body
            self.method_bodies[analyzer.node.name][meth.name] = methconverter.convert_method_body(meth, analyzer.node)
            self.method_names[data["name"]].append(meth.name)

    def get_classes(self) -> list[str]:
        """
        Get the list of class names.

        Returns:
        - List[str]: List of class names.
        """
        return self.classes

    def get_type_definitions(self) -> dict[str:str]:
        """
        Get the dictionary of type definitions.

        Returns:
        - Dict[str, str]: Dictionary of type definitions.
        """
        return self.type_definitions

    def get_class_by_name(self, name: str) -> dict[str:str]:
        """
        Get class information by name.

        Parameters:
        - name (str): Name of the class.

        Returns:
        - Dict[str, Union[str, Dict[str, str]]]: Class information.
        """
        if name in self.classes:
            class_data = {}
            class_data["name"] = name
            class_data["type definition"] = self.type_definitions[name]
            class_data["initializer method"] = self.init_methods[name]
            class_data["methods"] = {}
            meth_signatures = self.method_signatures[name]
            method_bodies = self.method_bodies[name]
            method_names = self.method_names[name]
            for methname in method_names:
                class_data["methods"][methname] = meth_signatures[methname] + "\n" + method_bodies[methname]

    def assemble(self) -> str:
        """
        Assemble Nim code for all classes.

        Returns:
        - str: Nim code for all classes.
        """
        string = "\n"
        
        for name in self.classes:
            string+="\n##########################################\n# " + f"   {name}   Type Definition  \n##########################################\n\n"
            string+=self.type_definitions[name]
            string+="\n##########################################\n#  " + f"   {name}  Initializer  \n##########################################\n\n"
            string+="\n"+self.init_methods[name]
            if len(self.method_names[name]) != 0:
                string+="\n##########################################\n# " + f"   {name}   Methods \n##########################################\n"
            for meth in self.method_names[name]:
                string+="\n"+self.method_signatures[name][meth]+"\n"
                string+=self.method_bodies[name][meth] + "\n\n"
        
        return string

    def show(self) -> None:
        """
        Display Nim code for all classes.
        """
        for name in self.classes:
            print(self.type_definitions[name])

            print("\n", self.init_methods[name])
            for meth in self.method_names[name]:
                print("\n", self.method_signatures[name][meth])
                #
                print(self.method_bodies[name][meth])



def convert_all_classes(filepath: str) -> ClassConverter:
    """
    Convert information about all classes in a Python file to Nim code.

    Parameters:
    - filepath (str): The path to the Python file.

    Returns:
    - ClassConverter: An instance of ClassConverter containing information about the classes.
    """
    nodes = get_python_nodes(filepath)
    class_nodes = [node for node in nodes if isinstance(node, ast.ClassDef)]
    converter = ClassConverter()
    for node in class_nodes:
        try:
            analyzed = ClassAnalyzer(node)
        except AttributeError as e:
            continue
        converter.add_class(analyzed)
    return converter


