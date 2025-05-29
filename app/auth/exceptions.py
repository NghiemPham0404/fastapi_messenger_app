from fastapi import HTTPException, status


class SignUpUserExist(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "User with this credential already exist",
            status_code = status.HTTP_409_CONFLICT
        )

class SignUpUserFail(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Sign up user fail",
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class LoginUserNotExist(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Your credential does not match any account",
            status_code = status.HTTP_404_NOT_FOUND
        )

class LoginWrongPassword(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Wrong password",
            status_code = status.HTTP_401_UNAUTHORIZED
        )

class RefreshTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Invalid token or expired token",
            status_code = status.HTTP_401_UNAUTHORIZED
    )