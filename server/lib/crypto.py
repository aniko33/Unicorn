import asyncio
import os

from Crypto.Cipher import Salsa20

class EncryptedTunnel:
    def __init__(self, r: asyncio.streams.StreamReader, w: asyncio.streams.StreamWriter, key: bytes, nonce: bytes) -> None:
        self.key = key
        self.nonce = nonce

        self.r = r
        self.w = w

    async def send(self, data: bytes):
        cipher = Salsa20.new(self.key, self.nonce)

        self.w.write(cipher.encrypt(data))
        await self.w.drain()

    async def recv(self, buffer: int) -> bytes:
        cipher = Salsa20.new(self.key, self.nonce)

        data = await self.r.read(buffer)
        return cipher.decrypt(data)
    
def get_hwid() -> str:
    if os.name == "nt":
        import subprocess
        return subprocess.getoutput("wmic csproduct get uuid")        
    else:
        return open("/etc/machine-id", "r").read().strip()