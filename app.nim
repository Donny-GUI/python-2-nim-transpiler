import std/strutils
import tables
import option
##  NonEssential Imports  ##
import os



##########################################
#  Functions  
##########################################

proc convertPythonSourceToNimSource(filepath: Option[string] = none[string], outfile: Option[string] = none[string]): None = 
  "\n  Convert a python source file to a nim source file by path string\n\n  Arguments:\n    filepath (str): path to the file to convert\n    outfile (str): path to the optional output file to write too.\n  Returns: nil\n  "
  echo("[py2nim]: Converting python source ", filepath)
  var start_string: string = "import std/strutils\nimport tables\nimport option\n"
  echo("[py2nim]: Getting imports...")
  import_strings = get_imports(filepath)
  if len(import_strings) != 0:
    start_string += "##  NonEssential Imports  ##\n"
  for impstr in import_strings:
    start_string += impstr + "\n"
  echo("[py2nim]: Converting python classes to nim types...")
  class_converter: ClassConverter = convert_all_classes(filepath)
  echo("[py2nim]: Assembling all methods and types...")
  string = class_converter.assemble()
  start_string += string
  echo("[py2nim]: Converting all functions....")
  func_converter: FunctionConverter = convert_all_functions(filepath)
  func_string = func_converter.assemble()
  start_string += func_string
  echo("[py2nim]: writing nim source...")
  bn = os.path.splitext(os.path.basename(filepath))[0]
  dn = os.path.dirname(filepath)
  bdn = os.path.basename(dn)
  newfile = dn + os.sep + bn + ".nim"
  if outfile == nil:
    if newfile.startsWith(os.sep):
      newfile = os.path.join(os.getcwd(), newfile[1:])
  else:
    newfile = outfile
  echo("[py2nim]: saving ", newfile)
  wfile.write(start_string)newfile)
  echo("[py2nim]: Starting revisions...")
  echo("[py2nim]: Fixing var assignments for strings")
  var_assignment_for_strings(newfile)
  echo("[py2nim]: Fixing var assignments for integers")
  var_assignment_for_integers(newfile)
  echo("[py2nim]: Fixing var assignments for @[]s")
  var_assignment_for_sequences(newfile)
  echo("[py2nim]: Fixing double quote glitch...")
  fix_weird_double_quote(newfile)
  echo("[py2nim]: Fixing proc types assignment")
  fix_proc_types(newfile)
  echo("[py2nim]: Fixing open with context managers")
  fix_nim_open_with(newfile)
  echo("[py2nim]: Done!")

proc convertPythonProject(): nil = 
  current_dir = os.getcwd()
  target_dir = replicate_directory_structure()
  for root, dirs, files in os.walk(os.path.join(current_dir, target_dir)):
    discard

proc applicationEntry(): nil = 
  global opt_args
  if len(opt_args) == 1:
    if opt_args[0] == "directory":
      for file in os.@[]dir():
        convert_python_source_to_nim_source(file)
    elif opt_args[0] == "project":
      convert_python_project()
    else:
      for file in opt_args:
        if os.path.exists(file):
          convert_python_source_to_nim_source(file)
        else:
          echo("[py2nim]: Cannot locate file: ", file)
