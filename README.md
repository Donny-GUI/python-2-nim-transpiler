# python-2-nim-transpiler
🎇Python 3.12 to Nim Transpiler

![Screenshot 2023-12-03 174056](https://github.com/Donny-GUI/python-2-nim-transpiler/assets/108424001/ef2109c7-54af-4526-943e-bf37558ee8eb)


# Current Progress
Within the python_module_maps.py file i am trying to map all the standard library modules to the nim equivalent (if possible).

if not possible:
   
   >create a template, type, macro or type ref by RootObj equivalent that can substitute in.
    

This will allow ```Complete Transpile``` of any python code within the standard library to nim. 

For non-standard library imports i am going to simply transpile them as needed. 

Hopefully this will make the transpilier completely operable with python moving forward and backwards.

#### This is going to take a long time.
I could really use some help.

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

6. Begin Import and Dependency conversion

   6.1 Get all standard lib imports

   6.2 Get all standard library import objects used by reference

   6.3 Get all standard library import FROM objects

   6.4 Use the python_module_maps.py file to substitute the nim equivalents i have set up.

7. Write source
   
