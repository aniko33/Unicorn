import socket



class User():
    def __init__(self, name:bytes, ip:str, handle):
        self.name = name.decode()
        self.uip=ip
        self.handle=handle
        print(self.name, self.uip)

class Session():
    def __init__(self):
        self.targets =[]