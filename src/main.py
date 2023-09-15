from sys import argv, stderr
from .error import had_error
from .tokenizer import TokenizerContext, StringTokenizer
from .parser import parse_token_list
from .evaluate import evaluate_stmt
from .ast import Stmt
from enum import Enum

tokenizer_context: TokenizerContext = TokenizerContext()

class ParsingResults(Enum):
    ok = 0
    error = 1
    retry = 2  # reached end of tokens during parsing - try adding the next line

def parse(code, interactive) -> tuple[ParsingResults, list[Stmt]]:
    global tokenizer_context
    saved_tokenizer_context = tokenizer_context.copy()

    tokens = StringTokenizer(tokenizer_context, code)
    tokens = tokens.scan_loop()

    if not interactive:
        tokenizer_context.on_eof()
    if tokenizer_context.block_comment_nesting:
        tokenizer_context = saved_tokenizer_context
        return ParsingResults.retry, []

    stmts = parse_token_list(tokens)
    if stmts is None:
        print("Failed due to parsing error", file=stderr)
        return ParsingResults.error, []
    elif isinstance(stmts, EOFError):
        return ParsingResults.retry, []

    return ParsingResults.ok, stmts

def execute(parse_result: list[Stmt]):
    try:
        for stmt in parse_result:
            evaluate_stmt(stmt)
    except:
        print("Runtime error", file=stderr)
        return False

    return True

class RunResults(Enum):
    ok = 0
    retry = 1
    error = 2

def run(code, interactive) -> RunResults:
    parse_result, parse_stmts = parse(code, interactive)

    if parse_result == ParsingResults.retry:
        return RunResults.retry

    if parse_result == ParsingResults.error or had_error:
        exit(1)

    assert(parse_result == ParsingResults.ok)
    exec_result = execute(parse_stmts)
    return RunResults.ok if exec_result else RunResults.error

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

        line += "\n"
        run_result = run(line, True)

        # If retry, extend the line, otherwise empty it
        if run_result == RunResults.retry:
            continue
        elif run_result == RunResults.error:
            exit(1)
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
