from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from models import conversations, messages, users, conversation_people
from db.database import engine
from routes.v1.auth import router as auth_router
from routes.v1.user import router as user_router
from routes.v1.conversation import router as conversation_router
from routes.v1.conversation_people import router as con_peo_router
from routes.v1.message import router as message_router
from routes.v1.contact import router as contact_router
from middleware import JWTAuthMiddleware
from fastapi.openapi.utils import get_openapi
from routes.v1.websocket import getChatRoomsManager,ChatRoomManager
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

users.Base.metadata.create_all(bind=engine)
conversations.Base.metadata.create_all(bind=engine)
conversation_people.Base.metadata.create_all(bind=engine)
messages.Base.metadata.create_all(bind=engine)

app.include_router(user_router)
app.include_router(message_router)
app.include_router(conversation_router)
app.include_router(con_peo_router)
app.include_router(auth_router)
app.include_router(contact_router)

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

# app.add_middleware(JWTAuthMiddleware)

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