from fastapi import FastAPI,  Depends, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from db.database import engine, Base
from api import include_routes
from middleware import configure_middleware
from fastapi.openapi.utils import get_openapi
from routes.v1.websocket import getChatRoomsManager,ChatRoomManager
from dotenv import load_dotenv

# load the enviroments variable
load_dotenv()

app = FastAPI()

# create entities in database or migrate database
Base.metadata.create_all(bind=engine)

# add middle ware
configure_middleware()

# add routes to application
include_routes(app)

# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title="My API",
#         version="1.0.0",
#         description="This API requires authentication via JWT token",
#         routes=app.routes,
#     )
#     openapi_schema["components"]["securitySchemes"] = {
#         "BearerAuth": {
#             "type": "http",
#             "scheme": "bearer",
#             "bearerFormat": "JWT"
#         }
#     }
#     openapi_schema["security"] = [{"BearerAuth": []}]
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

# app.openapi = custom_openapi


# configure websocket
@app.websocket("/ws/{conversation_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket,conversation_id:int, client_id: int, manager:ChatRoomManager = Depends(getChatRoomsManager)):
    await manager.connect(conversation_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Message text was: {data}")
    except WebSocketDisconnect:
        manager.disconnect(conversation_id, client_id, websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")