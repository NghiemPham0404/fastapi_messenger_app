from fastapi import HTTPException, status

class UserNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "User not found or being deleted",
            status_code = status.HTTP_404_NOT_FOUND
        )

class UserAlreadyExist(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "The user with this credentials already exists",
            status_code = status.HTTP_409_CONFLICT
        )

class UploadAvatarFail(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Upload avatar fail",
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        )