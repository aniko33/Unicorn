from datetime import datetime

def ansi(code: int) -> str:
    return f"\033[38;5;{code}m"

_reset  = "\033[0m"
_debug  = ansi(14)
_info   = ansi(12)
_warn   = ansi(11)
_error  = ansi(9)
_time   = ansi(13)

def current_time() -> str:
    return datetime.now().strftime("%H:%M:%S")

def debug(msg: str):
    print(f"[{_debug} DEBUG {_reset}:: {_time + current_time() + _reset} ]\t{msg}")

def info(msg: str):
    print(f"[{_info} INFO {_reset}:: {_time + current_time() + _reset} ]\t{msg}")

def warn(msg: str):
    print(f"[{_warn} WARN {_reset}:: {_time + current_time() + _reset} ]\t{msg}")

def error(msg: str):
    print(f"[{_error} ERROR {_reset}:: {_time + current_time() + _reset} ]\t{msg}")