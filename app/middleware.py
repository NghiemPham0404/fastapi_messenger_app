from fastapi import Depends, FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import os
from jose import jwt

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Middleware check if the Authorization is valid
class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Allow these endpoints without authentication
        if path.startswith("/static/"):
            return await call_next(request)
        
        # break part to parts 'api/user/1' = > ['api', 'user', '1']
        path_parts = request.url.path.strip("/").split("/") 
        # skip the versioning 'api/user/1' => '/user/1'
        sub_path = "/" + "/".join(path_parts[1:])

        # skip the public enpoint
        if sub_path in ["/","/docs", "/openapi.json","/favicon.ico","/auth/token","/auth/sign-up","/auth/refresh"]: 
            return await call_next(request)


        # Get Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

        # Extract token
        token = auth_header.split(" ")[1]

        try:
            # Decode token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user = payload  # Store user info in request state
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"detail":"Token has expired"})
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content={"detail":"Invalid token"})

        return await call_next(request)

def configure_middleware(app):
    """
    Add middlewares to application
    JWTAuthMiddleware : check if jwt is valid
    CORSMiddleware : configure the allowance requests to get info from application
    """
    app.add_middleware(JWTAuthMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # or specific IPs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],  # <== THIS MUST INCLUDE 'authorization'
    )

