import json

import compilers.python
import languages.language
import time
from os import system


# Debug functions
def annotate_mappings(new_struct, translated: str):
    """Get compiled text annotated with translated mappings"""
    compiled_result = ""
    last_compiled_index = 0
    last_translated_index = 0
    for mapping in new_struct.mappings:
        # (translated, compiled)
        compiled_result += new_struct.compiled[last_compiled_index:mapping[1]].replace("\n",
                                                                                       "\\n") + " /=/ " + translated[
                                                                                                          last_translated_index:
                                                                                                          mapping[
                                                                                                              0]].replace(
            "\n", "\\n") + "\n"

        last_compiled_index = mapping[1]
        last_translated_index = mapping[0]
    compiled_result += new_struct.compiled[last_compiled_index:].replace("\n", "\\n") + " /=/ " + translated[
                                                                                                  last_translated_index:].replace(
        "\n", "\\n") + "\n"

    return compiled_result


def compile(lang_dir: str, source_file: str, dest_file: str, debug_file: str):
    """Compile the code from the language in source to English Python in dest, saving the mappings in debug_file in JSON format if it's not None."""
    # Get language files
    language = languages.language.LanguageEnv(lang_dir)
    # Build the lexer and parser
    lexer = compilers.python.PythonLexer(language)
    lexer.build()
    parser = compilers.python.PythonParser(language, lexer)
    parser.build()
    # Run lexer and parser on source file
    with open(source_file, "r", encoding='utf8') as reader:
        src = reader.read()
    result = parser.parse(src)
    # Write compiled code
    with open(dest_file, "w", encoding='utf8') as writer:
        writer.write(str(result))

    # Write debug code
    """Format:
    "mappings": [[translated_index,compiled_index],...]",
    "line_mappings: [translated_line,...] """  # For each compiled line, 1-indexed
    if (debug_file is not None):
        debug_data = {}

        # Encode mappings
        mappings = result.mappings

        # Get line mappings
        lines = [None] + result.compiled.split("\n")
        len_lines = len(lines)
        next_i = 0
        line = 1
        translated_lines = [None] + src.split("\n")
        len_translated_lines = len(translated_lines)
        translated_line = 1  # 1-indexed
        translated_i = 0
        line_mappings = [0]  # Line 0 > 0
        for mapping in result.mappings:
            if (mapping[1] >= next_i):
                # Update translated line
                while (translated_i < mapping[0] and translated_line < len_translated_lines):
                    translated_line += 1
                    translated_i += len(translated_lines[translated_line - 1])
                # Add mapping
                line_mappings.append(translated_line - 1)  # Look for previous line
                # Update next_i - only 1 for each compiled line
                if (line < len_lines):
                    next_i += len(lines[line])
                    line += 1
                else:
                    # End Of File
                    break

        debug_data["mappings"] = mappings
        debug_data["line_mappings"] = line_mappings
        # Imported modules
        if("imported" in result.attr):
            debug_data["imported"] = result.attr["imported"]  # [[translated_module_path, location_path]...]
        else:
            debug_data["imported"] = []

        with open(debug_file, "w", encoding='utf8') as writer:
            json.dump(debug_data, writer)

# MAIN
start = time.time()
compile("languages/es", "source.py", "out.py", "debug.json")
end = time.time()
print(f"Took {end-start}s")


"""class Translator:

  tokens = {} # Override in language-specific translators
  
  def compile(self, source): # To English Python

    compiled = ""
    previous_tokens = []

    while (source != ""):
      for token in self.tokens:

        match = re.match(self.tokens[token], source)
        if (match):

          # Find string
          string = match.string[match.start():match.end()]

          compiled += self.translate_token_to_en(token, string, previous_tokens)

          # Update previous_tokens - reverse order
          previous_tokens = [(token, string)] + previous_tokens # Reverse order - latest at start

          # Update source - remove token read
          source = source[match.end():]
          break
      else:
        # Unrecognised character
        compiled += source[0]
        source = source[1:]
    
    return compiled
  
  def compile_file(self, filename):

    with open("source.py") as source_file:
	    source = source_file.read()
    
    return self.compile(source)
  
  def syntax_highlight_file(self, filename, colors):
    source_tokens = self.compile_file(filename)
    for token in source_tokens:
      print("\033[" + str(colors[token[0]]) + "m" + token[1] + "\033[0m", end="")  # Syntax-highlighted

class PythonTranslator(Translator):
  tokens = {
    "whitespace": "( |\t)+",
    "newline": "\n+",
    # Data
    "num": r"\d+(\.\d+)?j?",  # Number - j for complex
    "bool": r"True|False",  # Boolean
    "str": r'("[^"]*")|(`[^"]*")',  # String - fix later
    # Symbol / Operator
    "sym": r"\(|\)|\[|\]|{|}|(\+)|-|(\*)|/|==|<|>|<=|>=|=|:|\.|(and|or|not)(?=[^A-Za-z0-9_])|,",
    # Identifiers
    "kw":
    "(class|if|else|elif|while|for|in|def|import|from|as|break|continue|return)(?=[^A-Za-z0-9_])",  # Keyword
    "iden": r"[A-Za-z_]([A-Za-z0-9_])*(?=[^A-Za-z0-9_])",  # Identifier
    # Comment
    "comment": r"#[^\n]*\n"
  }

  def translate_token_to_en(self, token, string, previous_tokens):

    if(token == "kw"):
      # Keyword
      keywords = { # Currently from https://es.wikipedia.org/wiki/Categor%C3%ADa:Lenguajes_de_programación_en_español
        "if": "si",
        "else": "sino",
        "elif": "osi",
        "while": "mientras",
        "for": "para_cada",
        "in": "en",
        "def": "función",
        "import": "importar",
        "from": "de",
        "as": "como",
        "class": "clase",
        "return": "retornar"
      }
      if(string in keywords):
        return "\033[42m" + keywords[string] + "\033[0m"
      else:
        return "\033[41m" + string + "\033[0m"
    elif(token == "bool"):
      # Booleans
      booleans = {
        "True": "Verdadero",
        "False": "Falso"
      }
      if(string in booleans):
        return "\033[42m" + booleans[string] + "\033[0m"
      else:
        return "\033[41m" + string + "\033[0m"
    elif(token == "sym"):
      # Symbol / Operator
      operators = {
        "and": "y",
        "or": "o",
        "not": "no"
      }
      if(string in operators):
        return "\033[42m" + operators[string] + "\033[0m"
      else:      
        return string

    elif (token == "iden"):

      # Find identifier hierarchy - scan through previous tokens backwards, e.g. turtle.fd would give [("sym", "."), ("iden", "turtle")] when scanning "fd"
      hierarchy = []
      i = 0
      tokens_len = len(previous_tokens)

      while(i < tokens_len):
        token = previous_tokens[i]
        if(token[0] == "whitespace" or token[0] == "_err"):
          pass
        elif(token[0] == "sym" and token[1] == "."):
          # Found '.' - child of previous token
          i += 1
          token = previous_tokens[i]
          if(token[0] == "iden"):
            hierarchy.append(token[1])
          elif(token[0] == "str" or token[0] == "num" or token[0] == "bool"):
            hierarchy.append("." + token[0])

        else: 
          break # Unexpected character - likely beginning

        i += 1

      identifiers = {
        "": {
          # Built-in
          "print": "escribir",
          "input": "preguntar",

          "turtle": "tortuga"
        },
        "turtle": {
          "Turtle": "Tortuga",
          
          "forward": "avanzar",
          "fd": "avanzar",
          "backward": "atrás",
          "bk": "atrás",
          "left": "girar_isquierda",
          "lt": "isquierda",
          "right": "derecha",
          "rt": "girar_derecha",
          "penup": "sin_pluma",
          "pu": "sin_pluma",
          "pendown": "con_pluma",
          "pd": "con_pluma",
          "circle": "círculo",
          "speed": "velocidad",
          "pencolor": "color_de_pluma",
          "fillcolor": "color_de_relleno",
          "begin_fill": "empezar_relleno",
          "end_fill": "terminar_relleno"
        }
      }

      hierarchy.reverse()
      hierarchy = ".".join(hierarchy)

      try:
        return "\033[43m" + identifiers[hierarchy][string] + "\033[0m"
      except:
        return string
  
    else:
      return string


colors = {
    "whitespace": 0,
    "kw": 34,
    "iden": 0,
    "num": 32,
    "bool": 34,
    "str": 35,
    "sym": 36,
    "comment": 90,
    "_error": 41
}

pythonTranslator = PythonTranslator()
print(pythonTranslator.compile_file("source.py"))

"""
