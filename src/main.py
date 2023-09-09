from sys import argv, stderr
from .error import had_error
from .tokenizer import TokenizerContext, StringTokenizer
from .parser import parse_token_list, format_expresssion

tokenizer_context = TokenizerContext()
def parse(code):
    tokens = StringTokenizer(tokenizer_context, code)
    tokens = tokens.scan_loop()
    print("Tokens", tokens)
    expr = parse_token_list(tokens)
    print("Expr", format_expresssion(expr))

def execute(parse_result):
    # TODO
    return

def run(code):
    parse_result = parse(code)

    if had_error:
        exit(1)

    execute(parse_result)

def run_file(path):
    with open(path, "r") as file:
        code = file.read()
    run(code)
    tokenizer_context.on_eof()

def run_prompt():
    while True:
        try:
            line = input("> ")
        except EOFError:
            tokenizer_context.on_eof()
            break

        # TODO multi-line tokens in REPL are currently supported through a hack
        run(line + "\n")

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
