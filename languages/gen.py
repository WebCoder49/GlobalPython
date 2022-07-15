"""UI to generate python translation files by importing modules and indexing them"""
import importlib, json, os, inspect, copy


def index(obj, level, dependencies, imported_modules={}, base_classes=[]):
  """Index a package/module/class to return a dict of properties, removing props from specific base classes if necessary
  obj: Package to index
  level: 0, used in recursion
  dependencies: dependency array which will be filled with other required modules"""
  output = {}

  # Tuple of: Translated name, properties, args (None if not callable), (Inherits from / returns)?

  for property, value in inspect.getmembers(obj): # Remove prototype dunder
    # In base class?
    for base in base_classes:
      if (getattr(base, property, None) != None):
        # In base class - Remove
        break # Ignore this prop
    else:
      if(property[0] == "_"):
        # Private convention - don't index
        continue
      else:
        # Not removed - index

        if(callable(value) and not inspect.isclass(value)):
          # Function - get params
          params = []
          try:
            sig = inspect.signature(value)
            params = list(sig.parameters)
          except: pass # Cannot get annotation - use empty params

          output[property] = ("<name>", None, params)

        if(inspect.isclass(value)):
          # Class - inner properties, ignoring baseclass properties
          base_classes = value.__bases__

          # Index, ignoring inherited properties
          print(" "*level, "> Prop", property)
          inner = index(value, level+1, dependencies, imported_modules, base_classes)
          print(" "*level, "< Prop", property)

          # Constructor - get params
          params = []
          try:
            sig = inspect.signature(value.__init__)
            params = list(sig.parameters)[1:] # Don't include *self*
          except: pass # Cannot get annotation - use None

          # Get base classes
          base_class_names = []
          for base_class in base_classes:

            path = base_class.__qualname__.split(".")
            path.insert(0, base_class.__module__)  # @x = module x
            path.insert(0, ".PKG")


            base_class_names.append(path)
            # print(base_class.__qualname__, base_class.__qualname__.split("."))

          # Return
          output[property] = ("<name>", inner,  params, base_class_names) # Compiled name, Properties, Parameters, Base classes

        elif(inspect.ismodule(value)):
          # Module - inner properties; no parameters
          module_id = id(value) # Can be indentified uniquely
          if(not module_id in imported_modules):
            # Import module
            imported_modules[module_id] = value.__name__.split(".") # Absolute path
            imported_modules[module_id].insert(0, ".PKG")  # From package, not variable

            print(" "*level, f"{property} ({value.__name__}) needs to be imported")
            pkg = value.__name__.split(".")[0]
            if(pkg != pkg_name):
              # Import external package
              print(f"Import {property} from {imported_modules[module_id]}")
              # Another package is needed
              if(not pkg in dependencies):
                # Add new dependency
                dependencies.append(pkg)
              output[property] = ("<name>", None, None, [imported_modules[module_id]])  # Compiled name, Properties, Parameters, type
            else:
              # Local package - keep indexing
              output[property] = ("<name>", index(value, level+1, dependencies)) # Compiled name, Properties, Parameters, type
        else:
          # Other data - inherits type
          t = type(value)
          path = t.__qualname__.split(".")
          path.insert(0, t.__module__) # module x
          path.insert(0, ".PKG")  # module x
          output[property] = ("<name>", None, None, [path]) # Compiled name, Properties, Parameters, Type
    
  return output

# Import and retrieve module
language = input("Language: ")
if(not os.path.exists(f"languages/{language}")):
  os.mkdir(f"languages/{language}")
pkg_name = input("Package: ")

if(pkg_name == ""):
  pkg_name = "builtins"

pkg = importlib.import_module(pkg_name) # From PyPI

print("Loading", pkg)
print(f"To find more descriptions and docs for this package, see https://pypi.org/project/{pkg_name}/ (for third-party) or https://docs.python.org/3/library/{pkg_name}.html (for built-in)")

dependencies = []
data = (pkg_name, index(pkg, 0, dependencies))
print(dependencies)

with open(f"languages/{language}/{pkg_name}.json", "w") as writer:
  json.dump(data, writer, indent=2)
