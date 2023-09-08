from enum import Enum
from .error import error

TokenType = Enum("TokenType", [
    # Single-character tokens.
    "LEFT_PAREN", "RIGHT_PAREN", "LEFT_BRACE", "RIGHT_BRACE",
    "COMMA", "DOT", "MINUS", "PLUS", "SEMICOLON", "SLASH", "STAR",
    # One or two character tokens.
    "BANG", "BANG_EQUAL",
    "EQUAL", "EQUAL_EQUAL",
    "GREATER", "GREATER_EQUAL",
    "LESS", "LESS_EQUAL",
    # Literals.
    "IDENTIFIER", "STRING", "NUMBER",
    # Keywords.
    "AND", "CLASS", "ELSE", "FALSE", "FUN", "FOR", "IF", "NIL", "OR",
    "PRINT", "RETURN", "SUPER", "THIS", "TRUE", "VAR", "WHILE",
    "EOF"
])

class Token:
    token_type: TokenType
    lexeme: str
    literal: object
    line: int

    def __init__(self, token_type: TokenType, lexeme: str, literal: object, line: int):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self):
        return f"Token({str(self.token_type)}, {repr(self.lexeme)}, {repr(self.literal)}, {repr(self.line)})"

class TokenizerContext:
    # total line number
    line: int

    def __init__(self):
        self.line = 1

def is_digit(char: str) -> bool:
    if len(char) != 1: return False
    return ord("0") <= ord(char) and ord(char) <= ord("9")

def is_alpha(char: str) -> bool:
    if len(char) != 1: return False
    return (ord("a") <= ord(char) and ord(char) <= ord("z")) \
        or (ord("A") <= ord(char) and ord(char) <= ord("Z")) \
        or char == "_"

KEYWORD_TOKENS = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE
}

class StringTokenizer:
    # using a context stored across string tokenizers
    ctx: TokenizerContext
    # the string being tokenized
    code: str
    # start of the current token
    start: int
    # position in the code
    position: int
    # resulting list of tokens
    tokens: list[Token]

    def __init__(self, ctx: TokenizerContext, code: str):
        self.ctx = ctx
        self.code = code
        self.start = 0
        self.position = 0
        self.tokens = []

    def getc(self) -> str:
        self.position += 1
        return self.code[self.position - 1]

    def peek(self, count=0) -> str:
        if (self.position + count) >= len(self.code):
            return "EOF"
        return self.code[self.position + count]

    def match(self, expected: str) -> bool:
        return self.peek() == expected

    def add_token(self, token_type: TokenType, literal: object = None):
        text = self.code[self.start: self.position]
        self.tokens.append(Token(token_type, text, literal, self.ctx.line))

    def scan_string(self):
        while self.peek() not in ['"', "EOF"]:
            if self.peek() == "\n":
                self.ctx.line += 1
            self.getc()

        if self.peek() == "EOF":
            error("Unterminated string", line=self.ctx.line)
            return

        # Ignore closing "
        self.getc()

        # Trim surrounding quotes
        value = self.code[(self.start + 1): (self.position - 1)]
        self.add_token(TokenType.STRING, value)

    def scan_number(self):
        while is_digit(self.peek()):
            self.getc()

        # if it is a decimal
        if self.peek() == "." and is_digit(self.peek(1)):
            self.getc()  # consume .
            while is_digit(self.peek()):
                self.getc()  # consume digits

        text = self.code[self.start: self.position]
        self.add_token(TokenType.NUMBER, float(text))

    def scan_literal(self):
        while is_alpha(self.peek()) or is_digit(self.peek()):
            self.getc()
        text = self.code[self.start: self.position]
        if text in KEYWORD_TOKENS:
            self.add_token(KEYWORD_TOKENS[text])
        else:
            self.add_token(TokenType.IDENTIFIER)

    def block_comment(self):
        # ignore the *
        self.getc()
        # support nesting!
        block_quote_nesting = 1

        # We need one character of history
        def fail_on_eof():
            if self.peek() == "EOF":
                error("Unterminated block quote", line=self.ctx.line)
                return True
            return False

        if fail_on_eof(): return
        prev_char = self.getc()

        while block_quote_nesting > 0:
            # There shouldn't be an EOF before the block quote ends
            if fail_on_eof(): return
            char = self.getc()

            if prev_char == "/" and char == "*":
                # /* - increase nesting
                block_quote_nesting += 1
                # this character has been consumed - otherwise we'd have /*/
                char = ""
            elif prev_char == "*" and char == "/":
                # */ - decrease nesting
                block_quote_nesting -= 1
                # this character has been consumed - otherwise we'd have */*
                char = ""

            prev_char = char

    def scan_token(self):
        # mark token start
        self.start = self.position

        c = self.getc()
        if c == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif c == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ",":
            self.add_token(TokenType.COMMA)
        elif c == ".":
            self.add_token(TokenType.DOT)
        elif c == "-":
            self.add_token(TokenType.MINUS)
        elif c == "+":
            self.add_token(TokenType.PLUS)
        elif c == ";":
            self.add_token(TokenType.SEMICOLON)
        elif c == "*":
            self.add_token(TokenType.STAR)
        elif c == "!":
            if self.match("="):
                self.add_token(TokenType.BANG_EQUAL)
            else:
                self.add_token(TokenType.BANG)
        elif c == "=":
            if self.match("="):
                self.add_token(TokenType.EQUAL_EQUAL)
            else:
                self.add_token(TokenType.EQUAL)
        elif c == "<":
            if self.match("="):
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)
        elif c == ">":
            if self.match("="):
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)
        elif c == "/":
            if self.match("/"):
                # comment - no token
                while self.peek() not in ["EOF", "\n"]:
                    self.getc()
            elif self.match("*"):
                # block comment is complicated enough for a function
                self.block_comment()
            else:
                self.add_token(TokenType.SLASH)
        elif c == " " or c == "\r" or c == "\t":
            # ignore whitespace - no token
            pass
        elif c == "\n":
            # advance line number
            self.ctx.line += 1
        elif c == '"':
            self.scan_string()
        elif is_digit(c):
            self.scan_number()
        elif is_alpha(c):
            self.scan_literal()
        else:
            error("Unexpected character", line=self.ctx.line)

    def scan_loop(self):
        # scan tokens in a loop
        while self.position < len(self.code):
            self.scan_token()
        return self.tokens
