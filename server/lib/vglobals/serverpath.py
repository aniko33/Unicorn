from os import path, getcwd

CURRENT_PATH: str = path.realpath(getcwd())
CONFIG_PATH: str = path.join(CURRENT_PATH, "config")
LISTENERS_PATH: str = path.join(CURRENT_PATH, "listeners")
DIST_PATH: str = path.join(CURRENT_PATH, "dist")