from ply import lex, yacc
from ply.lex import Lexer

from collections import deque


class PushableLexer(): # Supports pushing of tokens for a lexer
  lexer = None
  def __init__(self, lexer:Lexer, eof_function):
    self.lexer = lexer
    self.eof_function = eof_function # For end-of-file

    # Add methods
    self.input = self.lexer.input
    self.lineno = self.lexer.lineno

  """Pushable"""
  pushed_queue = deque()
  queue_not_empty = False

  def token(self):
    # Either get from queue or lexer
    if(self.queue_not_empty):
      # Get new token from queue
      tok = self.pushed_queue.popleft()

      if(len(self.pushed_queue) <= 0):
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
  def t_newline(self,t):
    r'\n+'
    t.lexer.lineno += len(t.value)

  # Error handling
  def t_error(self,t):
    print(f"Illegal char @ line {t.lexer.lineno}: '{t.value[0]}'")
    t.lexer.skip(1)

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