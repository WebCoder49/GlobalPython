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
        self.scope_stack[0] = self.load_lib("")  # Built-in > Globals

        # print(f"Globals: {self.scope_stack[0]}")
        self.kw = self.load_lib(".kw")  # Keywords
        self.pkgs = self.load_lib(".pkgs")  # Package names
        self.literals = self.load_lib(".literals")  # Literals

    def load_lib(self, filename):
        """Get the parsed JSON data from the language folder with the specific filename (don't include the .json)."""
        # Find data file
        data_file = os.path.join(self.data_dir, filename + ".json")

        # Load as JSON
        with open(data_file, encoding='utf8') as reader:
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

    def get_properties_raw(self, property:str, parents:list=None):  # Automatically scope for parents = root
        """Get a property from a raw (compiled) name and list of possible parents"""

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
                if (property in props):
                    # Found property
                    results.append((tuple(p_path) + (property,), props[property]))
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
    scope_stack = [["", {}, None, []]]  # Global scope contains builtins and imported packages

    def scope_push(self, msg):
        """Add one more to stack"""
        self.scope_stack.append((msg, {}, None, []))
        # print("Scope push: ", msg, ">", self.scope_stack)
    def scope_pop(self):
        """Remove one from stack"""
        if(len(self.scope_stack) == 2):
            # Closed module
            with open(f"compilation_dump.json", "w", encoding="utf8") as writer:
                print("Dumping Data")
                json.dump(self.scope_stack[1], writer, indent=2)
        self.scope_stack.pop()

    def assign(self, iden_path, src, translated=None, simplify=True, override=True):
        """Assign the value src to the destination iden_path, in the local scope"""
        # print(f"[Assign] {iden_path} = {src}")
        if(simplify):
            new_src = []
            src_queue = deque(src)

            while(len(src_queue) > 0):
                source = src_queue.popleft()
                source_data = source[1]
                if(len(source_data) >= 4) and (source_data[1] is None or len(source_data[1]) == 0) and (len(source_data) < 3 or source_data[2] is None):
                    # Can simplify - Simplify source_data
                    for base in source_data[3]:
                        src_queue.append([base, self.raw_path_to_data(base)])
                else:
                    # Terminal - add to new_src
                    new_src.append(source)

            # print("\tSrc: ", src)
            src = new_src
            # print("\tNew Src: ", src)

        print("Assign", iden_path, "=", src)
        if (iden_path != src[0][0]):
            # Assign a variable name (so type can be remembered)

            dest = self.scope_stack[-1]  # Local

            for node in iden_path:
                properties = dest[1]
                if (not node in properties):
                    properties[node] = [node, {}, None, []]
                dest = properties[node]

            if(override):
                # New type
                for type in dest[3]:
                    del type

            for src_type in src:
                src_path = src_type[0]
                src_path = list(src_path)

                if(not src_path in dest[3]):
                    # Add to types if not in already
                    dest[3].append(src_path)

                if(translated != None):
                    dest[0] = translated # Add translated name

                # print("\t", dest)

        # print(dest)

    hiddentype_IDs = {}
    def hiddentype_get_next_ID(self, prefix):
        """Get the next available ID number for the hidden global - used when wanting invisible types to inherit from"""
        if(not prefix in self.hiddentype_IDs):
            self.hiddentype_IDs[prefix] = 1
            id = 0
        else:
            id = self.hiddentype_IDs[prefix]
            self.hiddentype_IDs[prefix] += 1

        return "." + prefix + "_" + str(id) # e.g. .list_0

    def hiddentype_save(self, id, data, scope=1):
        self.scope_stack[scope][1][id] = data  # Save in module-wide scope by default

    """Importing packages"""
    def import_lib(self, library, alias):
        """Import a library path and give a reference to it in alias"""

        # Import package (first part) hidden in globals
        translated_package = library[0]

        auto_alias = False
        if(translated_package in self.pkgs):
            package = self.pkgs[translated_package]
            if(alias == None):
                auto_alias = True # Translate alias name
                alias = (package,)
        else:
            print(self.pkgs)
            raise Exception(f"Package {translated_package} could not be found.")

        package_location = "." + package
        if(not package_location in self.scope_stack[0][1]):
            # Add package (hidden with .) to global scope
            self.scope_stack[0][1][package_location] = self.load_lib(package)

        # Assign whole path to alias
        self.assign(alias, ([(package_location,) + library[1:]],), translated_package if auto_alias else None)  # 1 possible path; no data needed; keep translated name if no alias

        return (package,) + library[1:]