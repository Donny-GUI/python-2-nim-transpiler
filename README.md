# python-2-nim-transpiler
🎇Python 3.12 to Nim Transpiler

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

5. Write source
   
