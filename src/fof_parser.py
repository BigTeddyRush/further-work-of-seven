from __future__ import annotations
from enum import Enum

class TokenType(Enum):
    UNKNOWN = 0
    EOF     = 1
    IDENTIFIER = 2

    FOR_ALL = '!'
    EXISTS  = '?'
    AND     = '&'
    OR      = '|'
    NOT     = '~'
    EQUAL   = '='
    COLON   = ':'
    COMMA   = ','
    L_PAREN = '('
    R_PAREN = ')'
    L_BRACKET = '['
    R_BRACKET = ']'

    IMPLIES = '=>'
    IF      = '<=>'

class Tokenizer:
    def __init__(self, text: str) -> None:
        self.index = 0
        self.text = text
        self.len = len(text)

    def next(self) -> tuple[TokenType, str]:
        # skip whitespaces
        while self.index < self.len and self.text[self.index].isspace():
            self.index += 1

        if self.index >= self.len:
            return (TokenType.EOF, '')
        
        type = TokenType.UNKNOWN
        start = self.index

        match self.text[self.index]:
            case _ if self.text[self.index].isalpha():
                while self.index < self.len and (self.text[self.index].isalnum() or self.text[self.index] == '_'):
                    self.index += 1
                type = TokenType.IDENTIFIER
            case '=' if self.index+1 < self.len and self.text[self.index+1] == '>':
                self.index += 2
                type = TokenType.IMPLIES
            case '<' if self.index+2 < self.len and self.text[self.index+1] == '=' and self.text[self.index+2] == '>':
                self.index += 3
                type = TokenType.IF
            case '!' | '?' | '&' | '|' | '~' | '=' | ':' | ',' | '(' | ')' | '[' | ']' as t:
                self.index += 1
                type = TokenType(t)
            case _:
                self.index += 1
        return (type, self.text[start:self.index]) # returns (type, lexeme)

# grammar
# formula    -> binary ;
# binary     -> unit ('<=>' | '=>') unit 
#             | unit ('|' unit)* 
#             | unit ('&' unit)* ;
# unit       -> unitary | '~' unit ;
# unitary    -> quantified | atomic | '(' formula ')' ;
# quantified -> ('!' | '?') '[' variable (',' variable)* ']' ':' unit ;
# atomic     -> predicate '(' term (',' term)* ')' | term '=' term ;
# term       -> variable | constant | function '(' term (',' term)* ')' ;
# predicate  -> lower_word ;
# function   -> lower_word ;
# constant   -> lower_word ;
# variable   -> A-Z (A-Z | a-z | 0-9 | '_')* ;
# lower_word -> a-z (A-Z | a-z | 0-9 | '_')* ;

class TreeNodeType(Enum):
    UNKNOWN      = 0
    QUANTIFIER   = 1
    BINARY       = 2
    BINARY_ASSOC = 3
    UNARY        = 4
    PREDICATE    = 5
    FUNCTION     = 6
    CONSTANT     = 7
    VARIABLE     = 8

class TreeNode:
    def __init__(self, type: TreeNodeType, value: str) -> None:
        self.children = []
        self.value = value
        self.type = type

    def append(self, child: TreeNode) -> TreeNode:
        self.children.append(child)
        return self

    def print(self, level:int=0, max_level:int=None):
        if max_level and level >= max_level:
            return

        print(' ' * 4 * level + str(self.type) + ": " + str(self.value))
        for child in self.children:
            child.print(level+1, max_level)

class FofParser():
    def __init__(self, tokens: list[tuple[TokenType, str]]) -> None:
        self.tokens = tokens
        self.current = 0

    def error(self, msg):
        raise SyntaxError(msg) 

    def current_type(self) -> TokenType:
        return self.tokens[self.current][0]

    def current_value(self) -> str:
        return self.tokens[self.current][1]

    def match(self, type: TokenType) -> bool:
        return  type == self.current_type()

    def advance(self) -> None:
        if not self.match(TokenType.EOF):
            self.current += 1

    def consume(self, type: TokenType, msg: str = None):
        if self.match(type):
            self.advance()
        else:
            self.error(msg or f"Error: expected {type} but got {self.current_type()}")

    def consume_identifier(self, type: TreeNodeType, msg: str = None):
        if self.current_type() != TokenType.IDENTIFIER:
            self.error(msg or f"Error: expected identifier but got {self.current_type()}")
            return

        if type == TreeNodeType.VARIABLE and self.current_value()[0].isupper():
            self.advance()
        elif (type == TreeNodeType.PREDICATE or type == TreeNodeType.FUNCTION) and self.current_value()[0].islower():
            self.advance()
        else:
            self.error(msg or f"Error: expected identifier of type {type}")

    def formula(self) -> TreeNode:
        return self.binary()
    
    def binary_assoc(self, op: TokenType, left: TreeNode) -> TreeNode:
        node = TreeNode(TreeNodeType.BINARY_ASSOC, self.current_value())
        node.append(left)

        while self.match(op):
            self.advance()
            node.append(self.unit())

        return node

    def binary(self) -> TreeNode:
        left = self.unit()

        if self.match(TokenType.IMPLIES) or self.match(TokenType.IF):
            node = TreeNode(TreeNodeType.BINARY, self.current_value())
            self.advance()

            return node.append(left).append(self.unit())

        if self.match(TokenType.OR) or self.match(TokenType.AND):
            return self.binary_assoc(self.current_type(), left)

        return left

    def unit(self) -> TreeNode:
        if self.match(TokenType.NOT):
            node = TreeNode(TreeNodeType.UNARY, '~')
            self.advance()

            return node.append(self.unit())

        return self.unitary()

    def unitary(self) -> TreeNode:
        if self.match(TokenType.L_PAREN):
            self.advance()
            node = self.formula()

            self.consume(TokenType.R_PAREN)
            return node

        if self.match(TokenType.FOR_ALL) or self.match(TokenType.EXISTS):
            return self.quantified()

        return self.atomic()

    def quantified(self) -> TreeNode:
        node = TreeNode(TreeNodeType.QUANTIFIER, self.current_value())
        self.advance()

        self.consume(TokenType.L_BRACKET)
        node.append(TreeNode(TreeNodeType.VARIABLE, self.current_value()))
        self.consume_identifier(TreeNodeType.VARIABLE)

        while self.match(TokenType.COMMA):
            self.advance()

            node.append(TreeNode(TreeNodeType.VARIABLE, self.current_value()))
            self.consume_identifier(TreeNodeType.VARIABLE)
        self.consume(TokenType.R_BRACKET)

        self.consume(TokenType.COLON)

        return node.append(self.unit())

    def atomic(self) -> TreeNode:
        node = self.term()

        # parse infix predicate
        if self.match(TokenType.EQUAL):
            self.advance()
            return TreeNode(TreeNodeType.PREDICATE, 'equal').append(node).append(self.term())

        if node.type == TreeNodeType.VARIABLE:
            self.error("Expected a predicate")

        node.type = TreeNodeType.PREDICATE
        return node
    
    def term(self) -> TreeNode:
        value = self.current_value()
        self.consume(TokenType.IDENTIFIER)

        if value[0].isupper():
            return TreeNode(TreeNodeType.VARIABLE, value)

        if self.match(TokenType.L_PAREN):
            self.advance()

            node = TreeNode(TreeNodeType.FUNCTION, value)
            while self.match(TokenType.IDENTIFIER):
                node.append(self.term())

                if self.match(TokenType.COMMA): self.advance()

            self.consume(TokenType.R_PAREN)
            return node

        return TreeNode(TreeNodeType.CONSTANT, value)

def parse_axiom(axiom: str) -> TreeNode:
    tokenizer = Tokenizer(axiom)
    tokens = []

    #type, lexeme = tokenizer.next()
    #tokens.append((type, lexeme))

    type, lexeme = TokenType.UNKNOWN, ""

    while type != TokenType.EOF:
        type, lexeme = tokenizer.next()
        tokens.append((type, lexeme))

    parser = FofParser(tokens)
    ast = parser.formula()
    parser.consume(TokenType.EOF)

    return ast

if __name__ == "__main__":
    ast = parse_axiom("![X,Y]: ((subclass(X,Y) & subclass(Y,X)) => ( X = Y ))")
    ast.print()