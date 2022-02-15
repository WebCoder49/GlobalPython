import json, os, time
from collections import deque


class LanguageEnv:
    """Class for loading language files into an environment and keeping variable names"""

    def print_data(self, path, data):
        """Get documentation data to display about an object"""
        # Translated name, properties, args (None if not callable), Inherits from / returns
        # Details

        # Translated Name
        translated_name = data[0]
        # Properties
        property_names = []
        if(len(data) > 1 and type(data[1]) is dict):
            for key in data[1]:
                prop = data[1][key]
                property_names.append(prop[0])

        # Arguments
        callable = False
        call_syntax = ""
        if (len(data) > 2 and type(data[2]) is list):
            callable = True
            params = data[2]
            call_syntax = f'({",".join(params)})'

        # Base classes / Inheritance
        inherits_from = []
        if (len(data) > 3 and type(data[3]) is list):
            for base_path in data[3]:
                inherits_from.append(".".join(base_path))


        return f"""
{translated_name}{call_syntax}
{"-" * len(translated_name)}
Callable: {("✔️" if callable else "❌")}
Properties: {", ".join(property_names) if len(property_names) > 0 else None}
Inherits from: {", ".join(inherits_from) if len(inherits_from) > 0 else None}

[Compiled Path (English): {" > ".join(path)}]
"""

    def __init__(self, data_dir):  # Programming language, e.g. py
        """Initialise environment for language files and load builtins
@param data_dir path identifier language files are stored in"""
        # Initialise root directory and saved translation strings
        self.data_dir = data_dir

        # Load built-in files and keywords
        # Globals
        self.scope_stack[0] = self.load_lib("")  # Built-in

        # print(f"Globals: {self.scope_stack[0]}")
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

    def raw_path_to_data(self, path:tuple):
        """From a raw (English) path, get the translation data (automatic scope)"""
        scopes = self.scope_stack[::-1] # Local scopes up tree
        # print("Scopes:", scopes)
        for scope in scopes:
            data = self.raw_path_to_data_scoped(path, scope)  # Local
            if(data != None):
                # print(f"Found {path} in scope {scope}")
                return data
            else:
                # print(f"Could not find path {path} in scope {scope}")
                pass

        return None # Not in scopes

    def raw_path_to_data_scoped(self, path: tuple, scope):
        """From a raw (English) path, get the translation data (for specific scope)"""
        possible_paths = deque([path])

        # Global
        while (len(possible_paths) > 0):
            # Get compilation data by path
            # scope = self.scope_stack[-1]  # Local

            data = scope

            path = possible_paths.popleft()

            # Try to find property
            for prop in path:
                # Get inner props
                props = data[1] if len(data) >= 2 else []
                # print("Prop", prop, props)
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

    def get_properties(self, property:str, parents:list=None):  # Automatically scope for parents = root
        """Get a property from a translated name and list of possible parents"""

        if(parents == None):
            # Path then data
            parents = self.scope_stack[::-1]  # All scopes, up tree
            parents = list(map(lambda parent: ("", parent), parents)) # Blank paths
            # print(f"Parents of scope are {parents}")

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
                        parent_queue.append((p_path, self.raw_path_to_data(base_class))) # From base class, but compiled w/ parent path

            else:
                # Not in parent
                continue
        return results

    """Variables and Scoping"""
    # Specific scopes identified via names
    scope_stack = [("", {}, None, [])]

    def scope_push(self, msg):
        """Add one more to stack"""
        self.scope_stack.append((msg, {}, None, []))
        # print("Scope push: ", msg, ">", self.scope_stack)
    def scope_pop(self):
        """Remove one from stack"""
        msg = self.scope_stack.pop()
        # print("Scope pop: ", self.scope_stack, "<", msg)

    def assign(self, iden_path, src):
        """Assign the value src to the destination iden_path, in the local scope"""

        # print("Assign", iden_path, "=", src)
        if (iden_path != src[0][0]):
            # Assign a variable name (so type can be remembered)

            dest = self.scope_stack[-1]  # Local

            for node in iden_path:
                properties = dest[1]
                if (not node in properties):
                    properties[node] = (node, {}, None, [])
                dest = properties[node]

            # New type
            for type in dest[3]:
                del type

            for src_type in src:
                src_path = src_type[0]
                dest[3].append(list(src_path))

        # print(dest)