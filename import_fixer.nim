import std/strutils
import tables
import option

    



##########################################
#  Functions  
##########################################

proc getImports(filename: Option[string] = none[string]): seq[string] = 
  "\n  Extract and convert import statements from a Python file.\n\n  Parameters:\n  - filename (str): The path to the Python file.\n\n  Returns:\n  - List[string]: List of converted import statements.\n  "
  content = read_file(f)
  tree = ast.parse(content)
  var strings: seq = @[]
  for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
      var name: string = "import " + string(node.module)
      try:
        val = importmap[name]
        strings.add(val)
      except KeyError:
        continue
    elif isinstance(node, ast.Import):
      names = node.names
      for n in names:
        var x: string = "import " + ast.unparse(n)
        try:
          val = importmap[x]
          strings.add(val)
        except KeyError:
          continue
  return strings
