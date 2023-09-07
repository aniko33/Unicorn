import asyncio, socket
from manager import Session, User
import utils
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from threading import Thread

session = Session()

style = Style.from_dict({
    '':          '#664e8f',

    # Prompt.
    'username': '#884444',
    'host':     '#00ffff bg:#444400',
    'underline':     'underline',
})


async def handle_client(client):
    loop = asyncio.get_event_loop()
    running = True
    username = (await loop.sock_recv(client, 2**18))
    session.targets.append(User(name=username.capitalize(), ip=client.getpeername()[0], handle=client))
    #while not running:
    #    request = (await loop.sock_recv(client, 2**18)).decode('utf8')
    #    response = request
    #    await loop.sock_sendall(client, response.encode('utf8'))

async def bind():
    print('x')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 9035))
    server.listen(2**18)
    server.setblocking(False)

    loop = asyncio.get_event_loop()

    while True:
        client, _ = await loop.sock_accept(server)
        loop.create_task(handle_client(client))

def cli():
    while True:
        try:
            cmd = prompt([('class:username','@> ')], completer=WordCompleter(utils.Commands.not_sel()), style=style)
            print(cmd)
        except KeyboardInterrupt:
            break
        except EOFError:
            break


x=Thread(target=cli)
y=Thread(target=asyncio.run, args=(bind(),))

x.start()
y.start()

x.join()
y.join()