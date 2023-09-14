from typing import List, Literal
from .tokenizer import Token, TokenType
from .error import error
from .ast import *

class UnrecognizedTokenError(Exception):
    token_error: Token
    token_error_msg: str

    def __init__(self, token):
        self.token_error = token
        self.token_error_msg = f"Parsing error, unrecognized token: {repr(token)}"
        super().__init__(self.token_error_msg)

class TokenStream:
    _tokens: List[Token]
    _pos: int

    def __init__(self, tokens: List[Token]):
        self._tokens = tokens
        self._pos = 0

    def __repr__(self):
        return f"TokenStream(pos={self._pos}, {repr(self._tokens)})"

    # have reached end
    def reached_end(self):
        return self._pos > len(self._tokens)

    # get next token or EOFError
    def next(self) -> Token:
        self._pos += 1

        if self.reached_end():
            raise EOFError()

        return self._tokens[self._pos - 1]

    # check the next token's type
    def check(self, token_type: TokenType) -> bool:
        if self._pos >= len(self._tokens):
            return False
        else:
            return self._tokens[self._pos].token_type == token_type

    # go to next if the next token type matches one of the given types
    def match(self, *token_types: TokenType) -> Token | Literal[False]:
        for token_type in token_types:
            if self.check(token_type):
                return self.next()

        return False

    # match which must work
    def consume(self, *token_types: TokenType) -> Token:
        match_result = self.match(*token_types)
        if match_result:
            return match_result
        else:
            # missing a character
            raise EOFError()


def left_associative_binary(next_precedence, *token_types: TokenType):
    def generated_function(token_stream: TokenStream) -> Expr:
        expr = next_precedence(token_stream)
        while op_token := token_stream.match(*token_types):
            right = next_precedence(token_stream)
            expr = BinaryExpr(expr, op_token, right)

        return expr

    return generated_function

def parse_primary(token_stream: TokenStream) -> Expr:
    if token_stream.match(TokenType.FALSE):
        return LiteralExpr(False)
    elif token_stream.match(TokenType.TRUE):
        return LiteralExpr(True)
    elif token_stream.match(TokenType.NIL):
        return LiteralExpr(None)
    elif op_token := token_stream.match(TokenType.NUMBER, TokenType.STRING):
        return LiteralExpr(op_token.literal)
    elif token_stream.match(TokenType.LEFT_PAREN):
        expr = parse_expression_top(token_stream)
        token_stream.consume(TokenType.RIGHT_PAREN)
        return GroupingExpr(expr)
    elif token_stream.reached_end():
        # expected to find something
        raise EOFError()
    else:
        # invalid token
        raise UnrecognizedTokenError(token_stream.next())

def parse_unary(token_stream: TokenStream) -> Expr:
    if op_token := token_stream.match(TokenType.BANG, TokenType.MINUS):
        right = parse_unary(token_stream)
        # not important enough to do a loop
        return UnaryExpr(op_token, right)

    return parse_primary(token_stream)

parse_factor     = left_associative_binary(parse_unary     , TokenType.SLASH, TokenType.STAR)
parse_term       = left_associative_binary(parse_factor    , TokenType.MINUS, TokenType.PLUS)
parse_comparison = left_associative_binary(parse_term      , TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL)
parse_equality   = left_associative_binary(parse_comparison, TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL)
parse_expression_top = parse_equality

def format_expresssion(format_expr: Expr) -> str:
    class FormatVisitor(VisitorInterface):
        def accept_binary_expr(self, expr: BinaryExpr):
            return parenthesize(expr.operator.lexeme, expr.left, expr.right)
        def accept_grouping_expr(self, expr: GroupingExpr):
            return parenthesize("group", expr.expression)
        def accept_literal_expr(self, expr: LiteralExpr):
            return str(expr.value)
        def accept_unary_expr(self, expr: UnaryExpr):
            return parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(name: str, *args: Expr) -> str:
        result = f"({name} "
        result += " ".join(arg.accept(FormatVisitor()) for arg in args)
        result += ")"
        return result

    return format_expr.accept(FormatVisitor())

# None is returned only on a real and registered parsing error
# EOF is recoverable if it's interactive
def parse_expression(token_stream: TokenStream) -> Expr | EOFError | None:
    try:
        return parse_equality(token_stream)
    except EOFError as e:
        return e
    except UnrecognizedTokenError as e:
        error(e.token_error_msg, e.token_error.line)
        return None

def parse_token_list(token_list: List[Token]) -> Expr | EOFError | None:
    return parse_expression(TokenStream(token_list))

