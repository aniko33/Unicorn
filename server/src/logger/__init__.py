from datetime import datetime

import sys

def ansi(code: int) -> str:
    return f"\033[38;5;{code}m"

_reset   = "\033[0m"
_success = ansi(10)
_debug   = ansi(6)
_info    = ansi(12)
_warn    = ansi(11)
_error   = ansi(1)
_fatal   = ansi(9)
_time    = ansi(13)

def current_time() -> str:
    return datetime.now().strftime("%H:%M:%S")

def success(msg: str, end = '\n'):
    sys.stderr.write(f"[{_success} SUCCESS {_reset}:: {_time + current_time() + _reset} ]\t{msg}"+end)

def debug(msg: str, end = '\n'):
    sys.stderr.write(f"[{_debug} DEBUG {_reset}:: {_time + current_time() + _reset} ]\t{msg}"+end)

def info(msg: str, end = '\n'):
    sys.stderr.write(f"[{_info} INFO {_reset}:: {_time + current_time() + _reset} ]\t{msg}"+end)

def warn(msg: str, end = '\n'):
    sys.stderr.write(f"[{_warn} WARN {_reset}:: {_time + current_time() + _reset} ]\t{msg}"+end)

def error(msg: str, end = '\n'):
    sys.stderr.write(f"[{_error} ERROR {_reset}:: {_time + current_time() + _reset} ]\t{msg}"+end)

def fatalerror(msg: str, end = '\n'):
    sys.stderr.write(f"[{_fatal} FATAL ERROR {_reset}:: {_time + current_time() + _reset} ]\t{msg}"+end)