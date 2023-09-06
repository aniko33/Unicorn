from fastapi import FastAPI
from utils.sessions import Sessions,User

sessions = Sessions()
sessions.victims = [User(name="unity"), User(name="aniko"), User(name="panda")]

app = FastAPI()

@app.get("/sessions")
async def getsessions():
    return {"sessions": sessions.victims}