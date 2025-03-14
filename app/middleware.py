from fastapi import Depends, FastAPI, Request, HTTPException, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import os
from jose import jwt

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/login", "/sign-up", "/docs","/openapi.json"]:  
            # Allow these endpoints without authentication
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
