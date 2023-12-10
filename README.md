# python-2-nim-transpiler
🎇Python 3.12 to Nim Transpiler

![Screenshot 2023-12-03 174056](https://github.com/Donny-GUI/python-2-nim-transpiler/assets/108424001/ef2109c7-54af-4526-943e-bf37558ee8eb)


# Getting Started ✨


## Windows Users 📎

Transpiling a python source file

```
git clone https://github.com/Donny-GUI/python-2-nim-transpiler.git
cd python-2-nim-transpiler
python app.py [yourFile.py]
```

## Linux Users 🐧

Transpiling a python source file

```
git clone https://github.com/Donny-GUI/python-2-nim-transpiler.git
cd python-2-nim-transpiler
python3 app.py [yourFile.py]
```

# Warning
This project is still in its testing phase. It is not for production use yet.


# TODO 
1. collections.namedtuple
2. list comprehensions
3. single-line print comprehensions
4. dictionary comprehensions
5. set comprehensions
6. Ternary operators
7. changing file permissions
8. map and filter builtins
9. Decorators
10. json small one offs
11. Self execution and main modules
12. unitest module
13. Docstring conversions
14. Optional indentation
15. async procs
16. Perhaps, make with open template?

# Transpile Workflow
The follow is  a description of the workflow for transpiling the python source to nim source 

1. Read the python source
2. Parse all the Class Definition nodes
   
   2.1. parse all class inits
   
   
   2.2. parse all the methods
   
   
   2.3. make the type definitions

   
   2.4. make the initializers
   
   
   2.5. make all the func methods
   
   
3. parse all the imports
   
   3.1. Map the imports to their nim equivalents
   
4. Parse all the python function nodes


   4.1. make all the function signatures


   4.2. make all the function bodies

5. Start fixing phase

   5.1 Fix variable assignments for strings, ints, sequences

   5.2 Fix Double quote glitch

   5.3 Fix proc type hints

   5.4 Fix Open with(filename, filemode) as fileReference blocks

7. Write source
   
