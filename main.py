import json

import compilers.python
import languages.language
import time
from os import system

# Get language files
start = time.time()
language = languages.language.LanguageEnv("languages/es")

# language.scope_in("Hello")
# language.scope_in("World")
# language.scope_out()
# language.scope_in("Global")
# language.scope_in("Python")
# language.scope_out()
# language.scope_out()
# language.scope_out()

# Build the lexer and parser
lexer = compilers.python.PythonLexer(language)
lexer.build()
parser = compilers.python.PythonParser(language, lexer)
parser.build()

# Run lexer and parser on source file
with open("source.py", "r", encoding='utf8') as reader:
	src = reader.read()
result = parser.parse(src)
end = time.time()


print(f"T: {end-start} (1/{int(1/(end-start))} of a second)")
# Write compiled code
with open("out.py", "w", encoding='utf8') as writer:
	writer.write(str(result))

# Run program UI
run_again = input("Program compiled. Run it? (Y/N) ").upper() != "N"
while run_again:
  print("--- Running Output ---")
  system("python out.py")
  print("--- End Of Program ---")
  run_again = input("Run again? (Y/N) ").upper() != "N"

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
        "True": "Verdad",
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
