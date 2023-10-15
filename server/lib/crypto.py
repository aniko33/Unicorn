import asyncio

from Crypto.Cipher import Salsa20

class EncryptedTunnel:
    def __init__(self, r: asyncio.streams.StreamReader, w: asyncio.streams.StreamWriter, key: bytes, nonce: bytes) -> None:
        self.r = r
        self.w = w

        self.cipher = Salsa20.new(key, nonce=nonce)

    async def send(self, data: bytes):
        self.w.write(self.cipher.encrypt(data))
        await self.w.drain()

    async def recv(self, buffer: int) -> bytes:
        data = await self.r.read(buffer)
        return self.cipher.decrypt(data)