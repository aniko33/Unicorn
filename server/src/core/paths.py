from os import path

BASE_PATH: str = path.join( path.sep, *__file__.split(path.sep)[1:-3] )
CONFIG_PATH: str = path.join(BASE_PATH, "config")
LISTENERS_PATH: str = path.join(BASE_PATH, "listeners")
DIST_PATH: str = path.join(BASE_PATH, "dist")