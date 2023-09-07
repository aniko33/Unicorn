import os

class BMKey:
    def new()->str:
        pure = os.urandom(256).hex()
        chunks = []
        for i in range(0, len(pure), 32):
            chunk = pure[i:i + 32]
            chunks.append(chunk)
        signature = "           #BM256-Sign\n"+("="*32)+"\n"+'\n'.join(chunks)+"\n"+("="*32)
        return signature
    
    def retrieve(signature:str)->bytearray:
        pure = signature.splitlines()
        del pure[0]; del pure[0]; pure.pop()
        return bytearray.fromhex(''.join(pure))

class Cipher():
    def __init__(self, key:str):
        pass