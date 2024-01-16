from sys import stdout

def ansi(code: int) -> str:
    return f"\033[{code}m"

def ansi_str(__text: str, code: int) -> str:
    return ansi(code) + __text + reset_ansi

reset_ansi = "\033[0m"

_alert = ansi_str("[!]", 91)
_warn = ansi_str("[@]", 93)
_info = ansi_str("[?]", 36)
_green = ansi_str("[+]", 32)
_red = ansi_str("[-]", 31)

def alert(*objs, end="\n", sep=" ", file=stdout, flush=False):
    file.write(_alert + " " + sep.join(map(str, objs)) + end)
    if flush:
        stdout.flush()

def warn(*objs, end="\n", start="", sep=" ", file=stdout, flush=False):
    file.write(start +_warn + " " + sep.join(map(str, objs)) + end)
    if flush:
        stdout.flush()

def info(*objs, end="\n", start="", sep=" ", file=stdout, flush=False):
    file.write(start + _info + " " + sep.join(map(str, objs)) + end)
    if flush:
        stdout.flush()

def green(*objs, end="\n", start="", sep=" ", file=stdout, flush=False):
    file.write(start + _green + " " + sep.join(map(str, objs)) + end)
    if flush:
        stdout.flush()
    

def red(*objs, end="\n", start="", sep=" ", file=stdout, flush=False):
    file.write(start + _red + " " + sep.join(map(str, objs)) + end)
    if flush:
        stdout.flush()