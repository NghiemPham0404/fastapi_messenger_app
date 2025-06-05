from fastapi import HTTPException, status


class NotGroupMember(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Unauthorized",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class GroupMemberNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Group member not found",
            status_code = status.HTTP_404_NOT_FOUND
        )

class CreateGroupMemberConflict(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Group member already exist",
            status_code = status.HTTP_409_CONFLICT
        )