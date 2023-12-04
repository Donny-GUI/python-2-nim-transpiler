import ast
from typer import TypeConverter
from class_analyzer import ClassAnalyzer
from method_converter import MethodConverter

from util import (
    get_python_nodes
)

   

class ClassData:
    def __init__(self, signature, type_definition, methods=[]) -> None:
        self.methods = methods
        self.type_definition = type_definition
        self.signature = signature

class ClassConverter(object):
    TypeMap = {
        "list": "seq",
        "dict": "Table[string, ?]",
        "int": "int",
        "str": "string",
        "bool":"bool",
        "tuple": "tuple",
        "set": "set",
        "complex": "complex",
        "float": "float",
    }
    class_properties = "name", "type definition", "initializer method", "methods"
    
    def __init__(self) -> None:
        self.classes = []
        self.procs = {}
        self.init_procs = {}
        self.type_definitions = {}
        self.method_signatures = {}
        self.method_bodies = {}
        self.init_methods = {}
        self.method_names = {}

    def get_data(self) -> list[ClassData]:
        datums = []
        for name in self.classes:
            meths = []
            for meth in self.method_names[name]:
                meths.append((self.method_signatures[name][meth], self.method_bodies[name][meth]))

            cd = ClassData(
                type_definition=self.type_definitions[name],
                signature=self.init_methods[name],
                methods=meths)
            
            datums.append(cd)
        
        return datums

    def add_class(self, analyzer: ClassAnalyzer) -> None:
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
        return self.classes

    def get_type_definitions(self) -> dict[str:str]:
        return self.type_definitions
    
    def class_properties_list(self) -> list[str]:
        return self.class_properties

    def get_class_by_name(self, name: str) -> dict[str:str]:
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

    def assemble(self):
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

    def show(self):
        for name in self.classes:
            print(self.type_definitions[name])

            print("\n", self.init_methods[name])
            for meth in self.method_names[name]:
                print("\n", self.method_signatures[name][meth])
                #
                print(self.method_bodies[name][meth])

def convert_all_classes(filepath: str) -> ClassConverter:
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


