from fastapi import FastAPI
from .auth.controller import router as auth_router
from .user.controller import router as user_router
from .group.controller import router as group_router
from .group_member.controller import router as group_member_router
from .message.controller import router as message_router
from .contact.controller import router as contact_router
from .conversation.controller import router as conversation_router

def include_routes(app : FastAPI):
    v1_routers = [auth_router,
                user_router,
                contact_router,
                group_router,
                group_member_router,
                conversation_router,
                message_router,
                ]
    for router in v1_routers:
        app.include_router(router, prefix="/v1")

    

