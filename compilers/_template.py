from ply import lex, yacc

class Lexer:
  def __init__(self, lang):
    self.lang = lang # Language handler
  
  # Build the lexer
  def build(self, **kwargs):
    self.lexer = lex.lex(module=self, **kwargs)

  # Test output
  def test(self, data):
    self.lexer.input(data)
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