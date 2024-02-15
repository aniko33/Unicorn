import os

def main(*args):
    os.system(" ".join((os.path.join(os.path.dirname(__file__), "upx"), *args)))
