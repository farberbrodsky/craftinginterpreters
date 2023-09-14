from sys import argv, stderr
from .error import had_error
from .tokenizer import TokenizerContext, StringTokenizer
from .parser import parse_token_list, format_expresssion
from .ast import Expr
from enum import Enum

tokenizer_context = TokenizerContext()

class ParsingResults(Enum):
    ok = 0
    error = 1
    retry = 2  # reached end of tokens during parsing - try adding the next line

def parse(code, interactive) -> tuple[ParsingResults, Expr]:
    tokens = StringTokenizer(tokenizer_context, code)
    tokens = tokens.scan_loop()
    if not interactive:
        tokenizer_context.on_eof()

    print("Tokens", tokens)
    expr = parse_token_list(tokens)
    if expr is None:
        print("Failed due to parsing error", file=stderr)
        return ParsingResults.error, Expr()
    elif isinstance(expr, EOFError):
        return ParsingResults.retry, Expr()

    print("Expr", format_expresssion(expr))
    return ParsingResults.ok, expr

def execute(parse_result):
    # TODO
    return

class RunResults(Enum):
    ok = 0
    retry = 1

def run(code, interactive) -> RunResults:
    parse_result, parse_expr = parse(code, interactive)

    if parse_result == ParsingResults.retry:
        return RunResults.retry

    if parse_result == ParsingResults.error or had_error:
        exit(1)

    assert(parse_result == ParsingResults.ok)
    execute(parse_expr)
    return RunResults.ok

def run_file(path):
    with open(path, "r") as file:
        code = file.read()
    run(code, False)
    tokenizer_context.on_eof()

def run_prompt():
    line = ""
    while True:
        try:
            line += input("> " if line else "$ ")
        except EOFError:
            tokenizer_context.on_eof()
            break

        run_result = run(line + "\n", True)

        # If retry, extend the line, otherwise empty it
        if run_result == RunResults.retry:
            continue
        else:
            line = ""
            assert(run_result == RunResults.ok)

def main():
    if len(argv) > 2:
        print(f"Usage: {argv[0] if len(argv) else 'main.py'} [script]", file=stderr)
        exit(1)
    elif len(argv) == 2:
        run_file(argv[1])
    else:
        run_prompt()

if __name__ == "__main__":
    main()
