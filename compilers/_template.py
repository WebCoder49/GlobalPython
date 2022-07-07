from ply import lex, yacc
from ply.lex import Lexer

from collections import deque
from copy import deepcopy

class PushableLexer(): # Supports pushing of tokens for a lexer
  lexer = None

  def __init__(self, lexer: Lexer, eof_function):
    self.lexer = lexer
    self.eof_function = eof_function  # For end-of-file

    # Add methods
    self.input = self.lexer.input
    self.lineno = self.lexer.lineno

  # Add properties - get,set
  @property  # new
  def lexpos(self):
    return self.lexer.lexpos

  @lexpos.setter
  def lexpos(self, val):
    self.lexer.lexpos = val

  """Pushable"""
  pushed_queue = deque()
  queue_not_empty = False

  def token(self):
    # Either get from queue or lexer
    if (self.queue_not_empty):
      # Get new token from queue
      tok = self.pushed_queue.popleft()

      if (len(self.pushed_queue) <= 0):
        self.queue_not_empty = False

    else:
      # Ask for next token from lexer
      tok = self.lexer.token()
      if(tok == None):
        # EOF
        tok = self.eof_function()

    return tok

  def push(self, tok):
    self.pushed_queue.append(tok)
    self.queue_not_empty = True

class Lexer:
  def __init__(self, lang):
    self.lang = lang # Language handler

  # Build the lexer
  def build(self, **kwargs):
    self.lexer = PushableLexer(lex.lex(module=self, **kwargs), self.eof)

  # Test output
  def test(self, data):
    self.lexer.input(data)
    whitespace = ["INDENT", "DEDENT"]
    colors = {
      "ID": 96,
      "STRING": 95,
      "OP": 93,
    }
    compiled_kws = set(self.keywords.values())

    while True:
      tok = self.lexer.token()
      if not tok:
        break
      color = 0
      if(tok.type in compiled_kws):
        color = 94
      elif(tok.type in colors):
        color = colors[tok.type]
      print(f"\033[{color}m" + tok.value + "\033[0m", end=" ")

      if (tok.type in whitespace):
        print(f"\033[90m[" + tok.type + "]\033[0m", end="")

  # Newlines
  def t_newline(self, t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    # t.lexer.lexpos = 0 # Start column

  # Error handling
  def t_error(self, t):
    print(f"Illegal char @ line {t.lexer.lineno}: '{t.value[0]}'")
    t.lexer.skip(1)


# Parsing object backbone for data storage
class ParsingStruct():
  """A structure to pass around possible types of expressions and hold the mappings between translated and compiled sources.
  Different types of structure will also use this to keep extra information."""

  def __init__(self, compiled: str = "", translated_pos=None):
    self.possible_paths = []  # List of pairs of (tuple path, list/tuple data from LanguageEnv)
    self.attr = {}  # Extra attributes of this struct

    # Add compiled value
    self.compiled = compiled
    self.mappings = []  # Mappings of (non-compiled pointers, compiled pointers)
    if (translated_pos != None):
      self.mappings.append((translated_pos, len(compiled)))  # At the end

  def __str__(self):
    """To convert to a string, return compiled code"""
    # Compiled code
    return getattr(self, "compiled", "")

  """Concatenation"""

  def __add__(self, other):
    """Concatenation of ParsingStructs and strings"""
    result = deepcopy(self)
    if (type(other) is str):
      # Add str value to result's compiled on right
      result.compiled += other
      # No change of pointers

    elif (type(other) is ParsingStruct):
      result.compiled += other.compiled
      result.attr.update(other.attr)

      len_left = len(self.compiled)
      for i, mapping in enumerate(other.mappings):
        result.mappings.append((mapping[0], mapping[1] + len_left))  # Add len of left to compiled pointer

    else:
      raise ArithmeticError(f"Cannot concatenate a '{type(other)}' to a ParsingStruct")

    return result

  def __radd__(self, other):
    """Concatenation of string on left to PStruct"""
    result = deepcopy(self)

    if (type(other) is str):
      # Add str value to result's compiled on left
      result.compiled = other + self.compiled

      len_left = len(other)
      for i, mapping in enumerate(result.mappings):
        result.mappings[i] = (mapping[0], mapping[1] + len_left)  # Add len of left to compiled pointer

    else:
      raise ArithmeticError(f"Cannot concatenate a ParsingStruct to a '{type(other)}'")

    return result

  """Indentation"""

  def indent(self):
    """Indent each line and update mappings"""
    # print("Indent", annotate_mappings(self))

    INDENT_SIZE = 4

    char_offset = INDENT_SIZE
    mapping_index = 0
    result_compiled = " " * INDENT_SIZE  # Indent size; no mapping changes

    for i, char in enumerate(self.compiled):
      if (char == "\n"):
        # Update mappings up to here
        mapping_index = self.update_mapping_index(mapping_index, i, char_offset)

        # Indent this line
        result_compiled += "\n" + " " * INDENT_SIZE
        char_offset += INDENT_SIZE
      else:
        result_compiled += char

      # Update mappings up to end
      mapping_index = self.update_mapping_index(mapping_index, i, char_offset)

      self.compiled = result_compiled

    # print("Indented", annotate_mappings(self))

  def update_mapping_index(self, mapping_index: int, upto_compiled_index: int, char_offset: int):
    """Update the mapping index by adding the char_offset to each mapping until the upto_compiled_index is reached."""
    if (char_offset != 0):
      while (mapping_index < len(self.mappings) and self.mappings[mapping_index][1] <= upto_compiled_index):
        # Add char_offset to mapping[1] (compiled mapping)
        self.mappings[mapping_index] = (
          self.mappings[mapping_index][0], self.mappings[mapping_index][1] + char_offset)
        mapping_index += 1

    return mapping_index

  @staticmethod
  def join(delimiter, structs):
    """Like str.join, but for non-string objects like ParsingStructs"""
    result = structs[0]  # First
    for struct in structs[1:]:
      # Others w/ delimiter first
      result += delimiter + struct

    return result


class Parser:
  def __init__(self, lang, lexer):
    self.lang = lang

    self.tokens = lexer.tokens
    self.lexer = lexer.lexer
    self.lexerclass = lexer

    self.parser = yacc.yacc(module=self)

  def build(self, **kwargs):
    self.parser = yacc.yacc(module=self, **kwargs)

  def parse(self, src):
    self.lexerclass.test(src)
    return self.parser.parse(src, self.lexer)

  # Error handling
  def p_error(self, p):
    raise SyntaxError(f"Syntax Error @ {p}")

  # Get position of lexer
  def p_getpos(self, p):
    """getpos :"""
    p[0] = self.lexer.lexpos
