from fastapi import FastAPI,  Depends, Path, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import engine, Base
from .api import include_routes
from .middleware import configure_middleware
from .websocket import getChatRoomsManager,ChatRoomManager
from dotenv import load_dotenv
from .config import custom_openapi

# load the enviroments variable
load_dotenv()

app = FastAPI()

# static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# templates folder
templates = Jinja2Templates("templates")

# add middle ware
configure_middleware(app)

# add routes to application
include_routes(app)


# create entities in database or migrate database
Base.metadata.create_all(bind=engine)

# openapi config for swagger-ui
app.openapi = lambda : custom_openapi(app)

# configure websocket
@app.websocket("/ws/{conversation_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket,
                            conversation_id:int, 
                            user_id: int, 
                            manager:ChatRoomManager = Depends(getChatRoomsManager)):
    token = websocket.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        print("Not found token in websocket request")
    else:
        print("found token in request")
    await manager.connect(conversation_id, user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_global(user_id, websocket)
        # await manager.broadcast(f"Client #{client_id} left the chat")


# default homepage
@app.get("/", name="home page")
def root(request : Request):
    return templates.TemplateResponse("index.html", {"request": request})