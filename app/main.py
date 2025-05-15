from fastapi import FastAPI,  Depends, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from .db.database import engine, Base
from .api import include_routes
from .middleware import configure_middleware
from fastapi.openapi.utils import get_openapi
from .routes.v1.websocket import getChatRoomsManager,ChatRoomManager
from dotenv import load_dotenv

# load the enviroments variable
load_dotenv()

app = FastAPI()

# add middle ware
configure_middleware(app)

# add routes to application
include_routes(app)


# create entities in database or migrate database
Base.metadata.create_all(bind=engine)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="This API requires authentication via JWT token",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    # openapi_schema["security"] = [{"BearerAuth": []}]
    for route in app.routes:
        if route.path not in ["/auth/token", "/auth/sign-up","/auth/refresh","/docs", "/openapi.json"]:
            if hasattr(route, "operation_id"):
                path = openapi_schema["paths"][route.path]
                for method in path:
                    path[method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


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
            data = await websocket.receive_text()
            print(f"Message text was: {data}")
    except WebSocketDisconnect:
        manager.disconnect_global(user_id, websocket)
        # await manager.broadcast(f"Client #{client_id} left the chat")