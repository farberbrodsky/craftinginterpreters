from sys import stderr

had_error = False

def error(msg, line=-1):
    global had_error
    # error prefix
    msg = f"Error: {msg}"

    # optional prefixes
    if line != -1:
        msg = f"[line {line}] {msg}"

    print(msg, file=stderr)
    had_error = True
