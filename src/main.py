from sys import argv, stderr
from .error import had_error

def parse(code):
    # TODO
    return

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

def run_prompt():
    while True:
        try:
            line = input("> ")
        except EOFError:
            break

        run(line)

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
