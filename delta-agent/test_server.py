#!/usr/bin/env python

import asyncio
import websockets
import rsa
import os

pub, priv = rsa.newkeys(1024)

async def echo(websocket, path):
    await websocket.recv()
    await websocket.send(rsa.PublicKey.save_pkcs1(pub))
    aeskey = await websocket.recv()
    print(rsa.decrypt(aeskey, priv))

start_server = websockets.serve(echo, "0.0.0.0", os.environ.get('PORT') or 8080)

print("WebSockets echo server starting", flush=True)
asyncio.get_event_loop().run_until_complete(start_server)

print("WebSockets echo server running", flush=True)
asyncio.get_event_loop().run_forever()
