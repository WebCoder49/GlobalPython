import copy

from ply import lex, yacc
from languages.language import LanguageEnv
from ._template import Lexer, Parser


class PythonLexer(Lexer):

  def __init__(self, lang:LanguageEnv):
    super().__init__(lang)
    # Register keywords
    self.keywords = lang.kw
    self.tokens += list(self.keywords.values())
    # print(self.tokens)
  
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
  indent_stack = [0]

  def indent_type(self, ind_size):
    last_indent = self.indent_stack[-1]
    if(ind_size > last_indent):
      self.indent_stack.append(ind_size)
      return -1 # Indent

    elif(ind_size < last_indent):
      # All dedents
      num_dedents = 0
      while(self.indent_stack[-1] > ind_size):
        self.indent_stack.pop()
        num_dedents += 1
      return num_dedents

    else:
      return 0

  def t_newline_blank(self, t): # Blank newline - don't interpret as indentation
    r'\n[ \t]*(?=\n|\#|$)'
    return None

  def t_newline(self, t):
    r'\n[ \t]*(?=[^ \t\n])' # $ means End Of File
    t.lexer.lineno += 1
    new_indent = len(t.value)-1

    indent_type = self.indent_type(new_indent)

    if(indent_type == -1):
      t.type = "INDENT"
      self.attributes["indentation"] = new_indent
    elif(indent_type > 0):
      t.type = "DEDENT"
      # Indent type is now dedent count
      if(indent_type > 1):
        dedent_tok = copy.copy(t)
        dedent_tok.value = ""
        for i in range(indent_type-1):
          self.lexer.push(dedent_tok)

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
  def p_module(self, p):
    '''module : scope_push codeblock scope_pop'''
    # With scope
    p[0] = p[2]

  def p_codeblock(self, p):
    '''codeblock : statement
                | codeblock statement
                | empty'''
    result = p[1]
    if(len(p) > 2):
      result.compiled += "\n" + p[2].compiled
    p[0] = result
  
  # Statement syntaxes

  # Large

  indentation = 4
  def indent(self, text):
    # Indent text
    result = ""
    for row in text.split("\n"):
      result += (" "*self.indentation) + row + "\n"

    return result

  def p_noexpkw(self, p):
    """noexpkw : ELSE"""
    p[0] = p[1] # No expression needed for these statements

  def p_withexpkw(self, p):
    """withexpkw : IF
                | ELIF
                | WHILE"""
    p[0] = p[1] # Expression needed for these statements

  def p_statement_withexpression(self, p):
      """statement : withexpkw expression ':' INDENT codeblock DEDENT"""
      # Block statement which needs expression
      p[0] = self.ParsingStruct()
      # Add main statement
      p[0].compiled = p[0].compiled = " ".join(map(str, p[1:4]))
      # Add codeblock
      p[0].compiled += "\n" + self.indent(p[5].compiled)

  def p_statement_noexpression(self, p):
      """statement : noexpkw ':' INDENT codeblock DEDENT"""
      # Block statement which does not need expression
      p[0] = self.ParsingStruct()
      # Add main statement
      p[0].compiled = p[0].compiled = " ".join(map(str, p[1:3]))
      # Add codeblock
      p[0].compiled += "\n" + self.indent(p[4].compiled)

  def p_statement_for(self, p):
      """statement : FOR path IN expression ':' INDENT codeblock DEDENT"""
      # For loop
      p[0] = self.ParsingStruct()

      # Evaluate path
      buffer = [None, p[2]]  # Store evaluation in
      self.p_expression_path(buffer)
      p[2] = buffer[0]

      # Add main statement
      p[0].compiled = p[0].compiled = " ".join(map(str, p[1:6]))
      # Add codeblock
      p[0].compiled += "\n" + self.indent(p[7].compiled)

  def p_statement_def(self, p):
      """statement : DEF expression '(' commaseparated ')' ':' scope_push INDENT codeblock DEDENT scope_pop"""
      # Function definition
      p[0] = self.ParsingStruct()
      # Add main statement
      p[0].compiled = p[0].compiled = " ".join(map(str, p[1:8]))
      # Add codeblock
      p[0].compiled += "\n" + self.indent(p[9].compiled)

  # Scoping - link to LanguageEnv

  def p_scope_push(self, p):
    """scope_push :"""
    self.lang.scope_push("Pushed")
    p[0] = "# Scope(" + str(self.lang.scope_stack) + ")"

  def p_scope_pop(self, p):
    """scope_pop :"""
    self.lang.scope_pop()

  # Small
  def p_statement_assignment(self, p):
    '''statement : path '=' expression'''
    
    p[0] = self.ParsingStruct() # No expression data kept as structure, not expression

    # Evaluate path
    buffer = [None, p[1]] # Store evaluation in
    self.p_expression_path(buffer)
    p[1] = buffer[0]

    p[0].compiled = " ".join(map(str, p[1:]))
    
    # Save variable name and type
    self.lang.assign(p[1].possible_paths[0][0], p[3].possible_paths)  # Path of language then dest

  def p_statement_expression(self, p):
    '''statement : expression'''
    p[0] = p[1]

  def p_statement_parsertest(self, p):
    '''statement : '=' expression '=' '''
    # print(f"\033[95mTesting on line {self.lexer.lineno}: {p[2]} is of type {p[2].possible_paths}\033[0m")
    
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
  def p_path_top(self, p):
    """path : ID"""

    # Terminal node of expression start - new expression struct
    result = self.ParsingStruct()
    result.compiled = "" # To add later

    result.possible_paths = self.lang.get_properties(p[1]) # Property p[1] from ROOT

    if(len(result.possible_paths) == 0):
      # Not defined - pass through unchanged anyway (in case is unindexed module var)
      # Add unchanged - Translated name, properties, args (None if not callable), (Inherits from / returns)?
      result.possible_paths.append(((p[1],), [p[1], None, None, self.literal_paths["_UNKNOWN"]]))
    else:
      pass # Wait later for compilation

    p[0] = result

  def p_path_expr_branch(self, p):
    """path : expression '.' ID"""
    paths = p[1].possible_paths
    for i in range(len(paths)):
      # Reset path of each path so only part after expression is added
      paths[i] = (tuple(), paths[i][1])
    self.p_path_branch(p)
  
  def p_path_branch(self, p):
    """path : path '.' ID"""
    
    # Expression hierarchy - w/ dot
    result = p[1]

    # print(p[1], ".", p[3], result.possible_paths)
    old_poss_paths = result.possible_paths
    result.possible_paths = self.lang.get_properties(p[3], result.possible_paths) # Property p[3] from p[1]'s result

    if(len(result.possible_paths) == 0):
      # Not defined - pass through unchanged anyway (in case is unindexed module var)
      for path in old_poss_paths:
        # Add unchanged - Translated name, properties, args (None if not callable), (Inherits from / returns)?
        result.possible_paths.append((path[0] + (p[3],), [p[3], None, None, self.literal_paths["_UNKNOWN"]]))
    else:
      pass  # Wait later for compilation

    p[0] = result

  def p_expression_path(self, p):
    """expression : path"""
    # Need to compile now
    result = p[1]

    # Choose arbitrary
    chosen = result.possible_paths[0] # Arbitrary
    chosen_path = chosen[0]

    result.possible_paths = [chosen]

    if(len(result.compiled) > 0):
      result.compiled += "." # After current compiled data
    result.compiled += ".".join(chosen_path)

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