from fastapi import HTTPException, status


class InvalidContactsList(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Invalid contact list request",
            status_code = status.HTTP_400_BAD_REQUEST
    )
        
class CreateContactConflict(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "user_id and contact_user_id must be different",
            status_code = status.HTTP_409_CONFLICT
    )
        
class CreateContactOtherNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "requested user not found",
            status_code = status.HTTP_404_NOT_FOUND
    )
        
class CreateContactExistConflict(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "requested contact already exist",
            status_code = status.HTTP_409_CONFLICT
    )
        
class ContactNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "contact not found or deleted",
            status_code = status.HTTP_404_NOT_FOUND
    )