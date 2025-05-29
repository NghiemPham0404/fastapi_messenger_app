from fastapi import HTTPException, status

class GroupNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Group not found or being deleted",
            status_code = status.HTTP_404_NOT_FOUND
        )