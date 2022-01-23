import json, os, time
from collections import deque


class LanguageEnv:
    """Class for loading language files into an environment and keeping variable names"""

    def print_data(self, name, data):
        """Get documentation data to display about an object"""
        # Compiled name, properties, args (None if not callable), Inherits from / returns
        # Details
        call_syntax = ""
        if len(data) >= 3 and type(data[2]) == list:  # Args
            args = ", ".join(data[2])
            call_syntax = f"({args})"

        return f"""
{name}{call_syntax}
{"-" * len(name)}
Callable: {("✔️" if len(data) >= 3 and type(data[2]) == list else "❌")}
Properties: {(", ".join(data[1].keys()) if len(data) >= 2 and type(data[1]) == dict and data[1] != {} else "None")}
Inherits from: {(",".join(map(".".join(data[3]))) if len(data) >= 4 and type(data[3]) == list else "None")}

[Compiled Name (English): {data[0]}]
"""

    def __init__(self, data_dir):  # Programming language, e.g. py
        """Initialise environment for language files and load builtins
@param data_dir path identifier language files are stored in"""
        # Initialise root directory and saved translation strings
        self.data_dir = data_dir

        # Load built-in files and keywords
        self.data = self.load_lib("")  # Built-in
        self.vars = ("", {})  # Empty - local vars
        self.kw = self.load_lib(".kw")  # Keywords
        self.literals = self.load_lib(".literals")  # Literals

    def load_lib(self, library):
        # Find library file
        lib_file = os.path.join(self.data_dir, library + ".json")
        # Load as JSON
        with open(lib_file, encoding='utf8') as reader:
            data = json.load(reader)
        return data

    """Getting properties"""

    def raw_path_to_data(self, path: tuple):
        """From a raw (English) path, get the translation data"""
        possible_paths = deque([path])
        while (len(possible_paths) > 0):
            # Get compilation data by path
            data = self.data

            path = possible_paths.popleft()

            # Try to find property
            for prop in path:
                # Get inner props
                props = data[1] if len(data) >= 2 else []
                if prop in props:
                    # Found property
                    data = props[prop]
                else:
                    break # Try base class
            else:
                return data

            # Not found - look in base classes
            if (len(data) >= 4 and not type(data[3]) is None):
                for base in data[3]:
                    possible_paths.append(base)

        return None  # Not found, most likely custom

    def get_properties(self, property, parents=None):  # Automatically self.data for parents = root
        """Get a property from a translated name and list of possible parents"""

        if(parents == None):
            # Path then data
            parents = [(tuple(), self.data)]
        results = []  # List of resulting possible properties

        parent_queue = deque(parents)
        while(len(parent_queue) > 0):
            p_path, parent = parent_queue.popleft()

            # Parent = reference to object
            if (parent != None):
                # Append the property data associated w/ it
                props = parent[1] if len(parent) >= 2 and (not parent[1] is None) else []

                # Get property
                for key in props:
                    if (props[key][0] == property):
                        # Found property
                        results.append((tuple(p_path) + (key,), props[key]))
                        break

                # Add base classes to queue
                if(len(parent) >= 4):
                    for base_class in parent[3]:
                        parent_queue.append((base_class, self.raw_path_to_data(base_class)))

            else:
                # Not in parent
                continue

        return results

    # def print_docs(self, find_str):
    #   find = find_str.split(".")
    #   compiled = [] # English name
    #   obj = (0, 0, self.data)
    #   # Follow hierarchy
    #   for property in find:
    #     if(type(obj[2]) != dict):
    #       # Hierarchy does not continue
    #       print(f"'{property}' not found")
    #       break
    #     elif(property in obj[2]):
    #       obj = obj[2][property] # Inner property
    #       compiled.append(obj[0])
    #     else:
    #       print(f"'{property}' not found")
    #       break
    #   else:
    #     print(self.print_data(find_str, obj))

    def local_assign(self, iden_path, type_path):
        print("Assign", iden_path, "=", type_path)
        if (iden_path != type_path):
            # Assign a custom local variable name (so type can be remembered)
            dest = self.data
            for node in iden_path:
                properties = dest[1]
                if (not node in properties):
                    properties[node] = (node, {}, None, [])
                dest = properties[node]

            dest[3].append(type_path)
