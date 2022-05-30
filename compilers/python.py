import copy

from ply import lex, yacc
from ply.lex import LexToken

from languages.language import LanguageEnv
from ._template import Lexer, Parser, ParsingStruct


class PythonLexer(Lexer):

    def __init__(self, lang: LanguageEnv):
        super().__init__(lang)
        # Register keywords
        self.keywords = lang.kw
        self.tokens += list(self.keywords.values())
        self.tokens += list(set(self.operators.values())) # Remove duplicates
        # print(self.tokens)

    attributes = {
        # Knowing current pos in translated code
        "indentation": 0,
    }

    # Literals
    literals = "()[]{}:,.="

    # Tokens
    tokens = [
        # Special
        "_GETPOS",
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
        r'(?!\d)(\w)(\w)*'  # Using \w allows accents, characters, etc. - not starting w/ digit
        if (t.value in self.keywords):
            # Is a keyword
            t.type = self.keywords[t.value]
            t.value = t.type.lower()
            # Word operators
            if (t.type in ["AND", "OR", "NOT", "IS"]):
                return self.t_OP(t)
        else:
            # Is an identifier
            t.type = 'ID'
        return t

    # Operators
    operators = {
        # Boolean
        "not": "OP_BOOL_UNARY",
        "and": "OP_BOOL",
        "or": "OP_BOOL",
        # Comparison
        "<": "OP_COMP",
        "<=": "OP_COMP",
        "==": "OP_COMP",
        ">=": "OP_COMP",
        ">": "OP_COMP",
        "is": "OP_COMP",
        "in": "OP_COMP",
        # Add
        "+": "OP_ADD",
        "-": "OP_ADD",
        # Multiply
        "*": "OP_MUL",
        "/": "OP_MUL",
        "%": "OP_MUL",
        "//": "OP_MUL",
        # Indices
        "**": "OP_IND"
    }
    def t_OP(self, t):
        r'[+\-*/%=<>]+'
        if(t.value == "="):
            t.type = t.value
        elif(t.value in self.operators):
            t.type = self.operators[t.value] # Add type
        return t

    # Indentation
    indent_stack = [0]

    def indent_type(self, ind_size):
        last_indent = self.indent_stack[-1]
        if (ind_size > last_indent):
            self.indent_stack.append(ind_size)
            return -1  # Indent

        elif (ind_size < last_indent):
            # All dedents
            num_dedents = 0
            while (self.indent_stack[-1] > ind_size):
                self.indent_stack.pop()
                num_dedents += 1
            return num_dedents

        else:
            return 0

    def t_newline_blank(self, t):  # Blank newline - don't interpret as indentation
        r'\n[ \t]*(?=\n|\#|$)'
        t.lexer.lineno += 1
        # t.lexer.lexpos = 0  # Start column
        return None

    def t_newline(self, t):
        r'\n[ \t]*(?=[^ \t\n])'  # $ means End Of File
        t.lexer.lineno += 1
        new_indent = max(0, len(t.value) - 1)

        indent_type = self.indent_type(new_indent)

        if (indent_type == -1):
            t.type = "INDENT"
            self.attributes["indentation"] = new_indent
        elif (indent_type > 0):
            t.type = "DEDENT"
            # Indent type is now dedent count
            if (indent_type > 1):
                dedent_tok = copy.copy(t)
                dedent_tok.value = ""
                for i in range(indent_type - 1):
                    self.lexer.push(dedent_tok)

            self.attributes["indentation"] = new_indent
        else:
            return None

        return t

    def eof(self):
        # End-of-file - indent to 0
        num_dedents = self.indent_type(0)
        for i in range(num_dedents):

            # Set up dedent token
            tok = LexToken()
            tok.value = ""
            tok.type = "DEDENT"

            # Indent type is now dedent count
            if (num_dedents > 1):
                dedent_tok = copy.copy(tok)
                dedent_tok.value = ""
                for i in range(num_dedents - 1):
                    self.lexer.push(dedent_tok)
            return tok

    t_ignore = " \t"

    # Comments
    def t_COMMENT(self, t):
        r'\#.*(?=\n|$)'  # $ means End Of File
        t.lexer.lineno += 1
        LexToken
        # Don't return to parser

    # Literals - Simple Datatypes

    # Booleans in identifiers
    # String
    def t_STRING(self, t):
        r'("""((.|\n))*?""")|(\'\'\'(.|\n)*?\'\'\')|(".*?")|(\'.*?\')'  # Non-greedy - find shortest possible outcome
        return t

    # Number
    def t_NUMBER(self, t):
        r'\d+(\.\d*)?j?'
        return t


class PythonParser(Parser):

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
        if (len(p) > 2):
            result += "\n" + p[2]
        p[0] = result

    # Statement syntaxes

    # Large

    indentation = 4

    def indent(self, text):
        # Indent text
        result = ""
        for row in text.split("\n"):
            result += (" " * self.indentation) + row + "\n"

        return result

    def p_noexpkw(self, p):
        """noexpkw : ELSE"""
        p[0] = ParsingStruct(p[1], self.lexer.lexpos)  # No expression needed for these statements

    def p_withexpkw(self, p):
        """withexpkw : IF
                | ELIF
                | WHILE"""
        p[0] = ParsingStruct(p[1], self.lexer.lexpos)  # Expression needed for these statements

    def p_statement_withexpression(self, p):
        """statement : withexpkw expression ':' INDENT codeblock DEDENT"""
        # Block statement which needs expression
        p[0] = ParsingStruct()
        # Add main statement
        p[0] = ParsingStruct.join(" ", p[1:4])
        # Add codeblock
        p[5].indent()
        p[0] += "\n" + p[5]

    def p_statement_noexpression(self, p):
        """statement : noexpkw ':' INDENT codeblock DEDENT"""
        # Block statement which does not need expression
        p[0] = ParsingStruct()
        # Add main statement
        p[0] = ParsingStruct.join(" ", p[1:3])
        # Add codeblock
        p[4].indent()
        p[0] += "\n" + p[4]


    def p_statement_for(self, p):
        """statement : start_for INDENT codeblock DEDENT"""
        # For loop
        p[0] = p[1]

        # Add codeblock
        p[3].indent()
        p[0] += "\n" + p[3]

    def p_start_for(self, p):
        """start_for : FOR path IN expression ':'"""
        p[0] = ParsingStruct()

        # Add item type
        item_path = p[2].possible_paths[0][0]  # 1st > Path
        item_type = self.lang.get_properties(".item", p[4].possible_paths, raw=True)  # .item hiddentype
        self.lang.assign(item_path, item_type)
        # print(f"[For - Assign] {item_path} = {item_type}")

        p[0] = ParsingStruct.join(" ", p[1:])


    def p_statement_def(self, p):
        """statement : DEF path '(' commaseparated ')' ':' scope_push INDENT codeblock DEDENT"""
        # Function definition
        p[0] = ParsingStruct()
        # Add main statement

        p[0] = ParsingStruct.join(" ", p[1:7])

        # Add codeblock
        p[9].indent()
        p[0] += "\n" + p[9]

        # Inside scope
        function_path = p[2].possible_paths[0][0]  # 1st > path
        function_returns = (('.returns',), self.lang.raw_path_to_data(('.returns',)))  # Saved as hidden local variable
        function_yields = (('.yields',), self.lang.raw_path_to_data(('.yields',)))  # Saved as hidden local variable

        # Process parameters

        params = []
        for param in p[4].attr["commaseparated_items"]:
            params.append(param.compiled)

        self.lang.scope_pop()  # Scope pop

        # Save outside scope
        self.lang.assign(function_path, [function_returns], None, True, False, params=params)  # Simplify; don't override
        if(function_yields[1] != None):
            self.lang.assign(function_path + (".item",), [function_yields], None, True, False)  # Simplify; don't override

        # print(self.lang.raw_path_to_data(function_path))

    def p_statement_return(self, p):
        '''statement : RETURN expression'''
        p[0] = ParsingStruct()  # No expression data kept as structure, not expression
        p[0] = ParsingStruct.join(" ", p[1:])

        self.lang.assign((".returns",), p[2].possible_paths, None, True)

    def p_statement_yield(self, p):
        '''statement : YIELD expression'''  # For generator functions
        p[0] = ParsingStruct()  # No expression data kept as structure, not expression
        p[0] = ParsingStruct.join(" ", p[1:])

        self.lang.assign((".yields",), p[2].possible_paths, None, True)

    # Scoping - link to LanguageEnv

    def p_scope_push(self, p):
        """scope_push :"""
        self.lang.scope_push("Pushed")

    def p_scope_pop(self, p):
        """scope_pop :"""
        p[0] = "# Popped Scope(" + str(self.lang.scope_stack[-1]) + ")"
        self.lang.scope_pop()

    # Small
    def p_statement_import(self, p):
        '''statement : IMPORT path
                  | IMPORT path AS path'''

        p[0] = ParsingStruct()  # No expression data kept as structure, not expression

        # Evaluate paths
        library = p[2].possible_paths[0][0]  # As tuple path
        alias = p[4].possible_paths[0][0] if len(
            p) >= 5 else None  # Default import alias is package name - dictated by languageEnv

        translated_pkg = self.lang.import_lib(library, alias)
        # print(translated_pkg)
        p[2].possible_paths[0] = (translated_pkg, p[2].possible_paths[0][1])
        p[0] = ParsingStruct.join(" ", p[1:])

    def p_statement_assignment(self, p):
        '''statement : path '=' expression'''

        p[0] = ParsingStruct()  # No expression data kept as structure, not expression

        p[0] = ParsingStruct.join(" ", p[1:])

        # Save variable name and type
        self.lang.assign(p[1].possible_paths[0][0], p[3].possible_paths)  # Path of language then dest

    def p_statement_expression(self, p):
        '''statement : expression'''
        p[0] = p[1]

    def p_statement_parsertest(self, p):
        '''statement : '=' expression '=' '''
        print(f"\033[95mTesting on line {self.lexer.lineno}: {p[2]} is of type {p[2].possible_paths}\033[0m")

        p[0] = ParsingStruct()

    """Expressions - `data` means w/o operations, whereas `expression` means with"""

    # Primitive Literals
    def get_literal(self, lit_name):
        # Return list of path, data
        result = []
        paths = self.literal_paths[lit_name]
        for path in paths:
            result.append([tuple(path), self.lang.raw_path_to_data(path)])
        return result

    def p_data_literal_string(self, p):
        """data : STRING"""

        # Terminal node of data start (but literal) - new data struct
        result = ParsingStruct(p[1], self.lexer.lexpos)
        result.possible_paths = self.get_literal("STRING")  # Turn lists into tuples and format
        p[0] = result

    def p_data_literal_number(self, p):
        """data : NUMBER"""

        # Terminal node of data start (but literal) - new data struct
        result = ParsingStruct(p[1], self.lexer.lexpos)
        result.possible_paths = self.get_literal("NUMBER")  # Turn lists into tuples and format
        p[0] = result

    # Main property hierarchy for linking to language env
    def p_path_top(self, p):
        """path : ID"""

        # Terminal node of data start - new data struct
        result = ParsingStruct("", self.lexer.lexpos)  # Get position of lexer

        result.possible_paths = self.lang.get_properties(p[1])  # Property p[1] from ROOT

        if (len(result.possible_paths) == 0):
            print(f"⚠️{(p[1],)} not defined.")
            # Not defined - pass through unchanged anyway (in case is unindexed module var)
            # Add unchanged - Translated name, properties, args (None if not callable), (Inherits from / returns)?
            result.possible_paths.append(((p[1],), [p[1], None, None, self.literal_paths["_UNKNOWN"]]))

        # Add path node
        result += result.possible_paths[0][0][-1]  # Last part

        p[0] = result

    def p_path_data_branch(self, p):
        """path : data '.' ID"""
        paths = p[1].possible_paths
        self.p_path_branch(p)

    def p_path_branch(self, p):
        """path : path '.' ID"""

        # Expression hierarchy - w/ dot
        result = p[1]

        # print(p[1], ".", p[3], result.possible_paths)
        old_poss_paths = result.possible_paths
        result.possible_paths = self.lang.get_properties(p[3],
                                                         result.possible_paths)  # Property p[3] from p[1]'s result

        if (len(result.possible_paths) == 0):
            # Not defined - pass through unchanged anyway (in case is unindexed module var)
            print(f"⚠️{p[1]}.{(p[3],)} not defined.")
            for path in old_poss_paths:
                # Add unchanged - Translated name, properties, args (None if not callable), (Inherits from / returns)?
                result.possible_paths.append((path[0] + (p[3],), [p[3], None, None, self.literal_paths["_UNKNOWN"]]))

        # Add path node
        result += "." + ParsingStruct(result.possible_paths[0][0][-1], self.lexer.lexpos)  # Last part

        p[0] = result

    # def evaluate_path(self, path: ParsingStruct):
    #     """Choose an arbitrary option of the possible paths and add it to the compiled result of a path Struct"""
    #
    #     # Choose arbitrary
    #     chosen = path.possible_paths[0]  # Arbitrary
    #     chosen_path = chosen[0]
    #
    #     path.possible_paths = [chosen]
    #
    #     if (len(path.compiled) > 0):
    #         path += "."  # After current compiled data
    #     path += ".".join(chosen_path)
    #
    #     return path

    def p_data_path(self, p):
        """data : path"""
        p[0] = p[1]

    # Expression-based syntaxes - no need to validate as Python does this

    def p_data_call(self, p):
        """data : data '(' commaseparated ')' """
        # Call data (e.g. str(3.14))
        result = p[1]

        # Remove parameters from paths as no need to call
        for poss_path in result.possible_paths:
            poss_path[1][2] = None  # Data > params

        result += ParsingStruct.join("", p[2:])
        p[0] = result

    # Operators
    def p_op_bool(self, p):
        """expression : bool OP_BOOL bool
                      | OP_BOOL_UNARY bool
                      | bool"""

        # HighExp : HighExp OP LowExp # Recurses on left of OP so evaluated from left
        #         | LowExp # Deeper level of operators (will be eval'd first, e.g. B deeper than I < D,M < A,S)

        self.op(p, type="OP_BOOL")

    def p_op_comp(self, p):
        """bool : sum OP_COMP sum
             | sum"""
        self.op(p, type="OP_COMP")

    def p_op_add(self, p):
        """sum : sum OP_ADD term
               | term"""
        self.op(p, type="OP_ADD")

    def p_op_mul(self, p):
        """term : term OP_MUL factor
               | factor"""
        self.op(p, type="OP_MUL")

    def p_op_ind(self, p):
        """factor : factor OP_IND data
               | OP_ADD data
               | data""" # Unary +/- or indices
        self.op(p, type="OP_IND")

    def p_data_paren(self, p):  # Parentheses
        """data : '(' expression ')' """
        result = p[2]
        result = "(" + result + ")"
        p[0] = result

    """Processing operators"""
    def op(self, p, type):
        """Process an operation to set the result."""
        if (len(p) == 2):
            p[0] = p[1]  # No processing
        elif (len(p) == 3):
            # Unary operator
            p[0] = self.op_unary(operator=p[1], operand=p[2], type=type)
        elif (len(p) == 4):
            # Binary operator
            p[0] = self.op_binary(operator=p[2], operand_1=p[1], operand_2=p[3], type=type)

            # print(f"[{type}]", list(map(lambda path: path[0], p[0].possible_paths)))

        # Add to compiled result
        p[0] = ParsingStruct.join(" ", p[1:])


    def op_unary(self, operator, operand, type):
        """Get the type of the result once a unary operator has been applied."""
        return operand

    def op_binary(self, operator, operand_1, operand_2, type): # TODO: Working on
        """Get the type of the result once a binary operator has been applied."""

        result = ParsingStruct()

        # Operators which return booleans
        if(type == "OP_BOOL" or type == "OP_COMP"):
            result.possible_paths = self.get_literal("BOOL")
        else:
            # Use heuristic rule:
            #   If 1st is int, return second
            #   Else return first
            for first_path in operand_1.possible_paths:
                for second_path in operand_2.possible_paths:
                    if(len(first_path[0]) == 1 and first_path[0][0] == "int"): # integer
                        if (not second_path in result.possible_paths):
                            result.possible_paths.append(second_path)
                    else:
                        if (not first_path in result.possible_paths):
                            result.possible_paths.append(first_path)

        return result

    # Structured Literals
    def process_iterable(self, item_struct:ParsingStruct, structure_type:str, result:ParsingStruct):
        """Create an iterable hiddentype with the correct item types using the commaseparated items, the type of structure needed and the result ParsingStruct to save it in."""
        # Add sub-items' possible paths
        item_poss_paths = []
        for item in item_struct.attr["commaseparated_items"]:
            poss_paths = item.possible_paths
            for poss_path in poss_paths:
                if (not poss_path in item_poss_paths):
                    item_poss_paths.append(poss_path)

        # print("[process_iterable] A", structure_type, "of", " or ".join(map(lambda item: ".".join(item[0]), item_poss_paths)))

        # Change to base classes by removing data and leaving path
        for i in range(len(item_poss_paths)):
            item_poss_paths[i] = item_poss_paths[i][0]

        # Add hiddentype to extend from
        this_id = self.lang.hiddentype_request_ID(structure_type)
        this_type = (this_id[-1], {}, None, self.literal_paths[structure_type])  # Dynamic
        this_type[1][".item"] = [".item", {}, None, item_poss_paths]  # Inner > Hidden local item

        self.lang.hiddentype_save(this_id, this_type)

        # Extend from hiddentype
        result.possible_paths = [[this_id, this_type]]  # 1 possible path - path then data

    def p_data_literal_list(self, p):
        """data : '[' commaseparated ']' """

        # Terminal node of data start (but literal) - new data struct
        result = ParsingStruct()

        self.process_iterable(p[2], "LIST", result)

        result = ParsingStruct.join("", p[1:])
        p[0] = result

    def p_data_literal_tuple(self, p):
        """data : '(' commaseparated ')' """

        # Terminal node of data start (but literal) - new data struct
        result = ParsingStruct()

        self.process_iterable(p[2], "TUPLE", result)

        result = ParsingStruct.join("", p[1:])
        p[0] = result

    # Common syntax structures
    def p_commaseparated(self, p):
        """commaseparated : expression
                      | commaseparated ',' expression
                      | commaseparated ','
                      | empty"""  # (Left)>Right

        # Create result from first
        if (len(p) < 4):
            # From expression
            if (p[1] is None):
                result = ParsingStruct()
            else:
                result = ParsingStruct.join("", p[1:])
            result.attr["commaseparated_items"] = [p[1]]
        else:
            # Adding on to prev.
            result = ParsingStruct.join("", p[1:])
            result.attr["commaseparated_items"].append(p[3])

        p[0] = result

    def p_empty(self, p):
        """empty :"""
        pass
