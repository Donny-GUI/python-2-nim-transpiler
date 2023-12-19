import ast
import re 

from .sys import FunctionMap as SysFunctionMap
from .os import FunctionMap as OSFunctionMap
from .datetime import FunctionMap as DateTimeFunctionMap
from .time import FunctionMap as TimeFunctionMap

from .string import MandatoryStringImports, PythonStringConstants

DotReference = re.compile(r'^[a-z]*\.[A-Za-z]*$')

ModuleFunctionMap = {
    "os": OSFunctionMap,
    "sys": SysFunctionMap,
    "datetime": DateTimeFunctionMap,
    "time": TimeFunctionMap,
    "string": PythonStringConstants
}


class ModuleConverter(object):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        with open(self.filepath, "r") as f:
            self.content = f.read()

        self.modules = []
        self.from_modules = []
        self.from_imports = []
        
        for node in ast.walk(ast.parse(self.content)):
            if isinstance(node, ast.ImportFrom):
                self.from_imports.append([x.name for x in node.names])
                for name in node.names:
                    self.from_modules.append(name.name)
            
            if isinstance(node, ast.Import):
                for name in node.names:
                    self.modules.append(name.name)

        self.all_modules = self.modules + self.from_modules

    def get_replacement(self, refobj):
        try:
            modmap = ModuleFunctionMap.get(refobj.split('.')[0])
            return modmap.get(refobj)
        except:
            return refobj 
        
    def convert_modules(self, fp: str):

        with open(fp, "r") as f:
            nimcontent = f.read()
        
        dot_references = DotReference.finditer(nimcontent)
        for ref in dot_references:
            refobjs = ref.string.split('.')
            if refobjs[0] in self.all_modules:
                nimcontent = re.sub(ref.string, self.get_replacement(ref.string), nimcontent)
        
        with open(fp, "w") as f:
            if "string" in self.all_modules:
                f.writelines(MandatoryStringImports)
            f.write(nimcontent)


        
        