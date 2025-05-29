from fastapi import HTTPException, status

class NotAuthorized(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Unauthorized",
            status_code = status.HTTP_401_UNAUTHORIZED
    )