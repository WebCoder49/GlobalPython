from ._template import Lexer, Parser

class PythonLexer(Lexer):

  def __init__(self, lang):
    super().__init__(lang)
    # Register keywords
    self.keywords = lang.kw
    self.tokens += list(self.keywords.values())
    print(self.tokens)
  
  attributes = {
    "indentation": 0
  }

  # Literals
  literals = "()[]{}:,.="

  # Tokens
  tokens = [
    # Structure
    "INDENT",
    "DEDENT",
    "COMMENT",
    # Literals
    "STRING",
    "NUMBER",
    # Identifiers; Operators
    "ID",
    "OP"
  ]
  
  # Keywords
  def t_ID(self, t):
    r'(?!\d)(\w)(\w)*' # Using \w allows accents, characters, etc. - not starting w/ digit
    if(t.value in self.keywords):
      # Is a keyword
      t.type = self.keywords[t.value]
      t.value = t.type.lower()
      # Word operators
      if(t.type in ["AND", "OR", "NOT", "IS"]):
        t.type = "OP"
    else:
      # Is an identifier
      t.type = 'ID'
    return t
  
  # Operators
  def t_OP(self, t):
    r'[+\-*/%=]+'
    if(t.value == "="):
      # Assignment - not normal operator
      t.type = "="
    return t

  # Indentation
  def t_newline(self, t):
    r'\n[ \t]*(?=[^ \t]|$)' # $ means End Of File
    t.lexer.lineno += 1
    new_indent = len(t.value)-1

    if(new_indent > self.attributes["indentation"]):
      t.type = "INDENT"
      self.attributes["indentation"] = new_indent
    elif(new_indent < self.attributes["indentation"]):
      t.type = "DEDENT"
      self.attributes["indentation"] = new_indent
    else: return None

    return t
  
  t_ignore = " \t"
  
  # Comments
  def t_COMMENT(self, t):
    r'\#.*(?=\n|$)' # $ means End Of File
    # Don't return to parser

  # Literals - Simple Datatypes

  # Booleans in identifiers
  # String
  def t_STRING(self, t):
    r'("""((.|\n))*?""")|(\'\'\'(.|\n)*?\'\'\')|(".*?")|(\'.*?\')' # Non-greedy - find shortest possible outcome
    return t

  # Number
  def t_NUMBER(self, t):
    r'\d+(\.\d*)?j?'
    return t





class PythonParser(Parser):
  # Parsing object backbone for data storage
  class ParsingStruct():
    def __str__(self):
      # Compiled code
      return getattr(self, "compiled", "")
    pass

  def __init__(self, lang, lexer):
    super().__init__(lang, lexer)
    # Register keywords
    self.literal_paths = lang.literals


  # Main structure
  def p_codeblock(self, p):
    '''codeblock : statement
                | codeblock statement
                | empty'''
    result = p[1]
    if(len(p) > 2):
      result.compiled += "\n" + p[2].compiled
    p[0] = result
  
  # Statement syntaxes
  def p_statement_assignment(self, p):
    '''statement : ID '=' expression'''
    
    p[0] = self.ParsingStruct() # No expression data kept as structure, not expression
    p[0].compiled = " ".join(map(str, p[1:]))
    
    # Save variable name and type
    self.lang.local_assign((p[1],), p[3].possible_paths[0][0][0])

  def p_statement_expression(self, p):
    '''statement : expression'''
    p[0] = p[1]

  def p_statement_parsertest(self, p):
    '''statement : '=' expression '=' '''
    print(f"Testing on line {self.lexer.lineno}: ", p[2], "is of type", p[2].possible_paths)
    
    p[0] = self.ParsingStruct()
    p[0].compiled = ""
  
  """Expressions"""

  # Primitive Literals
  def get_literal(self, lit_name):
    # Return list of path, data
    result = []
    paths = self.literal_paths[lit_name]
    for path in paths:
        result.append((tuple(path), self.lang.raw_path_to_data(path)))
    return result

  def p_expression_literal_string(self, p):
    """expression : STRING"""
    
    # Terminal node of expression start (but literal) - new expression struct
    result = self.ParsingStruct()
    result.possible_paths = self.get_literal("STRING") # Turn lists into tuples and format
    result.compiled = p[1]
    p[0] = result

  def p_expression_literal_number(self, p):
    """expression : NUMBER"""
    
    # Terminal node of expression start (but literal) - new expression struct
    result = self.ParsingStruct()
    result.possible_paths = self.get_literal("NUMBER") # Turn lists into tuples and format
    result.compiled = p[1]
    p[0] = result
  
  # Main property hierarchy for linking to language env
  def p_expression_top(self, p):
    """expression : ID"""

    # Terminal node of expression start - new expression struct
    result = self.ParsingStruct()

    result.possible_paths = self.lang.get_properties(p[1]) # Property p[1] from ROOT

    if(len(result.possible_paths) == 0):
      # Not defined - pass through unchanged anyway (in case is unindexed module var)
      result.compiled = p[1] # Name unchanged
    else:
      result.compiled = result.possible_paths[0][1][0] # First path > data > compiled name

    p[0] = result
  
  def p_expression_branch(self, p):
    """expression : expression '.' ID"""
    
    # Expression hierarchy - w/ dot
    result = p[1]

    print(p[1], ".", p[3], result.possible_paths)
    result.possible_paths = self.lang.get_properties(p[3], result.possible_paths) # Property p[3] from p[1]'s result

    if(len(result.possible_paths) == 0):
      # Not defined - pass through unchanged anyway (in case is unindexed module var)
      result.compiled += "." + p[3] # Name unchanged
    else:
      result.compiled += "." + result.possible_paths[0][1][0] # First path > data > compiled name

    p[0] = result

  # Expression-based syntaxes - no need to validate as Python does this
    
  def p_expression_call(self, p):
    """expression : expression '(' commaseparated ')' """
    # Call expression (e.g. str(3.14))
    result = p[1]
    result.compiled += "".join(map(str, p[2:]))
    p[0] = result

  def p_expression_op(self, p): # Operators
    """expression : expression OP expression"""
    result = p[1]
    result.compiled += " " + " ".join(map(str, p[2:]))
    p[0] = result

  def p_expression_paren(self, p): # Parentheses
    """expression : '(' expression ')' """
    result = p[2]
    result.compiled = "(" + result.compiled + ")"
    p[0] = result

    
  # Structured Literals
  def p_expression_literal_list(self, p):
    """expression : '[' commaseparated ']' """
    
    # Terminal node of expression start (but literal) - new expression struct
    result = self.ParsingStruct()
    result.possible_paths = (tuple(map(tuple, self.literal_paths["LIST"])),) # Turn lists into tuples and formats
    result.compiled = "".join(map(str, p[1:]))
    p[0] = result

  def p_expression_literal_tuple(self, p):
    """expression : '(' commaseparated ')' """
    
    # Terminal node of expression start (but literal) - new expression struct
    result = self.ParsingStruct()
    result.possible_paths = (tuple(map(tuple, self.literal_paths["TUPLE"])),) # Turn lists into tuples and formats
    result.compiled = "".join(map(str, p[1:]))
    p[0] = result
    
  # Common syntax structures
  def p_commaseparated(self, p):
    """commaseparated : expression
                      | commaseparated ',' expression
                      | empty"""  # (Left)>Right
    
    result = self.ParsingStruct()
    if(p[1] == None):
      result.compiled = ""
    else:
      result.compiled = "".join(map(str, p[1:]))
    p[0] = result
  
  def p_empty(self, p):
    """empty :"""
    pass