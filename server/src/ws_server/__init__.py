from . import broadcast
import logger

from websockets import server
import asyncio
import ssl as _ssl

async def _run(ip: str, port: int, ssl=False, ssl_context=()):
    ws_ssl_context = None
    
    if ssl:
        ws_context = _ssl.SSLContext(_ssl.PROTOCOL_TLS_SERVER)
        ws_context.load_cert_chain(*ssl_context)

    async with server.serve(broadcast.whandler, ip, port, ssl=ws_ssl_context):
        logger.debug(f"Websocket server started: {ip}:{port}")
        await asyncio.Future()

def run(*args):
    asyncio.run(_run(*args))
