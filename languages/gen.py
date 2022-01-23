"""UI to generate python translation files by importing modules and indexing them"""
import importlib, json, os, inspect, copy

def index(obj):
  """Index a package/module/class to return a dict of properties"""
  output = {}

  # Tuple of: Translated name, properties, args (None if not callable), (Inherits from / returns)?

  for property, value in inspect.getmembers(obj): # Remove prototype dunder
    if(property[0:2] != "__"):

      if(callable(value) and not inspect.isclass(value)):
        # Function - get params
        params = []
        try:
          sig = inspect.signature(value)
          params = list(sig.parameters)
        except: pass # Cannot get annotation - use empty params

        output[property] = ("<name>", None, params)

      elif(property[0] != "_"):
        if(inspect.isclass(value)):
          # Class - inner properties, ignoring baseclass properties
          base_classes = value.__bases__

          # Remove baseclass props
          inner = index(value)
          for iden in copy.copy(inner):
            for base in base_classes:
              if(getattr(base, iden, None) != None):
                # In base class - Remove
                del inner[iden]
          
          # Constructor - get params
          params = []
          try:
            sig = inspect.signature(value.__init__)
            params = list(sig.parameters)[1:] # Don't include *self*
          except: pass # Cannot get annotation - use None

          # Get base classes
          base_class_names = []
          for base_class in base_classes:
            base_class_names.append(base_class.__qualname__.split("."))
            print(base_class.__qualname__, base_class.__qualname__.split("."))

          # Return
          output[property] = ("<name>", inner,  params, base_class_names) # Compiled name, Properties, Parameters, Base classes

        elif(inspect.ismodule(value)):
          # Module - inner properties; no parameters
          output[property] = ("<name>", index(value)) # Compiled name, Properties
          
        else:
          # Other data - inherits type
          output[property] = ("<name>", None, None, type(value).__qualname__.split(".")) # Compiled name, Properties, Parameters, Type

    
  return output

# Import and retrieve module
language = input("Language: ")
if(not os.path.exists(f"languages/{language}")):
  os.mkdir(f"languages/{language}")
module_name = input("Module: ")
if(module_name == ""):
  module = __builtins__
else:
  module = importlib.import_module(module_name) # From PyPI

print("Loading", module)
print(f"To find more descriptions and docs for this module, see https://pypi.org/project/{module_name}/ (for third-party) or https://docs.python.org/3/library/{module_name}.html (for built-in)")

data = (module_name, index(module))

with open(f"languages/{language}/{module_name}.json", "w") as writer:
  json.dump(data, writer, indent=2)
