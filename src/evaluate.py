from .ast import *
from .tokenizer import TokenType

def is_equal(obj1: object, obj2: object) -> bool:
    return obj1 == obj2

def is_truthy(obj: object) -> bool:
    if obj is None or (isinstance(obj, bool) and not obj):
        return False
    else:
        return True

class ExprEvalVisitor(ExprVisitorInterface):
    def accept_binary_expr(self, expr: BinaryExpr):
        left_eval = expr.left.accept(self)
        right_eval = expr.right.accept(self)

        if expr.operator.token_type == TokenType.MINUS or \
           expr.operator.token_type == TokenType.SLASH or \
           expr.operator.token_type == TokenType.STAR:
            assert(type(left_eval) is float)
            assert(type(right_eval) is float)
            if expr.operator.token_type == TokenType.MINUS:
                return left_eval - right_eval
            elif expr.operator.token_type == TokenType.SLASH:
                return left_eval / right_eval
            elif expr.operator.token_type == TokenType.STAR:
                return left_eval * right_eval

        elif expr.operator.token_type == TokenType.PLUS:
            if (type(left_eval) is float) and (type(right_eval) is float):
                return left_eval + right_eval
            elif (type(left_eval) is str) and (type(right_eval) is str):
                return left_eval + right_eval
            else:
                assert(0)

        elif expr.operator.token_type == TokenType.GREATER or \
             expr.operator.token_type == TokenType.GREATER_EQUAL or \
             expr.operator.token_type == TokenType.LESS or \
             expr.operator.token_type == TokenType.LESS_EQUAL:
                 assert(type(left_eval) is float)
                 assert(type(right_eval) is float)
                 if expr.operator.token_type == TokenType.GREATER:
                     return left_eval > right_eval
                 elif expr.operator.token_type == TokenType.GREATER_EQUAL:
                     return left_eval >= right_eval
                 elif expr.operator.token_type == TokenType.LESS:
                     return left_eval < right_eval
                 elif expr.operator.token_type == TokenType.LESS_EQUAL:
                     return left_eval <= right_eval
        elif expr.operator.token_type == TokenType.BANG_EQUAL or \
             expr.operator.token_type == TokenType.EQUAL_EQUAL:
                 if expr.operator.token_type == TokenType.BANG_EQUAL:
                     return not is_equal(left_eval, right_eval)
                 elif expr.operator.token_type == TokenType.EQUAL_EQUAL:
                     return is_equal(left_eval, right_eval)

        else:
            assert(0)

    def accept_grouping_expr(self, expr: GroupingExpr):
        return expr.expression.accept(self)

    def accept_literal_expr(self, expr: LiteralExpr):
        return expr.value

    def accept_unary_expr(self, expr: UnaryExpr):
        right_eval = expr.right.accept(self)

        if expr.operator.token_type == TokenType.MINUS:
            assert(type(right_eval) is float)
            return -right_eval
        elif expr.operator.token_type == TokenType.BANG:
            return not is_truthy(right_eval)
        else:
            assert(0)

# singleton object
EXPR_EVAL = ExprEvalVisitor()

class StmtEvalVisitor(StmtVisitorInterface):
    expr_eval: ExprEvalVisitor
    def __init__(self):
        self.expr_eval = ExprEvalVisitor()

    def accept_expression_stmt(self, stmt: ExpressionStmt):
        stmt.expression.accept(self.expr_eval)

    def accept_print_stmt(self, stmt: PrintStmt):
        print(stmt.expression.accept(self.expr_eval))

# singleton object
STMT_EVAL = StmtEvalVisitor()

# singleton helper
def evaluate_expression(expr: Expr) -> object:
    return expr.accept(EXPR_EVAL)

# singleton helper
def evaluate_stmt(stmt: Stmt) -> None:
    stmt.accept(STMT_EVAL)
