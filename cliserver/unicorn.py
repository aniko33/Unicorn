import asyncio
import utils
import rsa

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from threading import Thread

from manager import Session, User, AES256GCM
from bm import AES256GCM

CONNECTION_LIMIT = 20
BUFFERSIZE = 1024 # 1kb
session = Session()

style = Style.from_dict({
    '':          '#664e8f',

    # Prompt.
    'username': '#884444',
    'host':     '#00ffff bg:#444400',
    'underline':     'underline',
})

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    pub, priv = rsa.newkeys(1024)

    await reader.read(BUFFERSIZE)
    await writer.write(rsa.PublicKey.save_pkcs1(pub))
    writer.drain()

    (key, iv) = await rsa.decrypt(reader.read(BUFFERSIZE), priv).split("&")

    aes = AES256GCM(reader, writer, key, iv)

    await aes.send(b"1")

    username = await aes.recv(BUFFERSIZE)
    client_addr = writer.get_extra_info("peername")
    client_socket = writer.get_extra_info("socket")
    session.targets.append(User(username.capitalize(), client_addr, client_socket))

async def bind():
    print('x')

    server = await asyncio.start_server(handle_client, "0.0.0.0", 9035)
    async with server:
        await server.serve_forever()

def cli():
    while True:
        try:
            cmd = prompt([('class:username','@> ')], completer=WordCompleter(utils.Commands.not_sel()), style=style)
            print(cmd)
        except KeyboardInterrupt:
            break
        except EOFError:
            break

async def main(): 
    threads = []
    threads.append(Thread(target=cli))
    threads.append(Thread(target=asyncio.run, args=(bind(),)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    asyncio.run(main())