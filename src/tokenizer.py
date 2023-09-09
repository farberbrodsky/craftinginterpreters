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
    # block comment nesting: >0 if in a block comment
    block_comment_nesting: int
    # in a multiline string
    in_string: bool
    # multiline string context
    string_context: str

    def __init__(self):
        self.line = 1
        self.block_comment_nesting = 0
        self.in_string = False
        self.string_context = ""

    def on_eof(self):
        if self.block_comment_nesting != 0:
            error("Unterminated block quote", line=self.line)
        elif self.in_string:
            error("Unterminated string", line=self.line)

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
        # create context
        was_in_string = self.ctx.in_string
        if not self.ctx.in_string:
            self.ctx.in_string = True
            self.ctx.string_context = ""

        # advance until " or EOF
        while self.peek() not in ['"', "EOF"]:
            if self.peek() == "\n":
                self.ctx.line += 1
            self.getc()

        # Trim surrounding quotes
        value = self.code[(self.start + (0 if was_in_string else 1)): self.position]
        self.ctx.string_context += value
        print("value", repr(value), repr(self.code))

        # in case of EOF: keep context
        if self.peek() == "EOF":
            return

        # Ignore closing "
        self.getc()

        self.add_token(TokenType.STRING, self.ctx.string_context)
        # Reset context
        self.ctx.in_string = False
        self.ctx.string_context = ""

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
        # We need one character of history
        def is_pre_eof():
            return self.peek() == "EOF"

        if is_pre_eof(): return
        prev_char = self.getc()

        while self.ctx.block_comment_nesting > 0:
            # There shouldn't be an EOF before the block quote ends
            if is_pre_eof(): return
            char = self.getc()

            if prev_char == "/" and char == "*":
                # /* - increase nesting
                self.ctx.block_comment_nesting += 1
                # this character has been consumed - otherwise we'd have /*/
                char = ""
            elif prev_char == "*" and char == "/":
                # */ - decrease nesting
                self.ctx.block_comment_nesting -= 1
                # this character has been consumed - otherwise we'd have */*
                char = ""

            prev_char = char

    def scan_token(self):
        # mark token start
        self.start = self.position

        if self.ctx.block_comment_nesting > 0:
            # still in a block comment
            self.block_comment()
            return
        elif self.ctx.in_string:
            # still in a string
            self.scan_string()
            return

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
                # ignore the *
                self.getc()
                # support nesting!
                self.ctx.block_comment_nesting = 1
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
