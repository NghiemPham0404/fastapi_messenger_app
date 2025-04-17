from routes.v1.auth import router as auth_router
from routes.v1.user import router as user_router
from routes.v1.conversation import router as conversation_router
from routes.v1.conversation_people import router as con_peo_router
from routes.v1.message import router as message_router
from routes.v1.contact import router as contact_router

def include_routes(app):
    app.include_router(user_router)
    app.include_router(message_router)
    app.include_router(conversation_router)
    app.include_router(con_peo_router)
    app.include_router(auth_router)
    app.include_router(contact_router)

    

