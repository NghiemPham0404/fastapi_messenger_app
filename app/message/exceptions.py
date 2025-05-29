from fastapi import HTTPException, status

class SendMessageForbiden(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Forbidden",
            status_code = status.HTTP_403_FORBIDDEN
        )

class SendMessageFail(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Send message request failed",
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class MessageNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Message not found",
            status_code = status.HTTP_404_NOT_FOUND
        )

class UpdateMessageFail(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "Update message request failed",
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class EditMessageTimeout(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "can not edit message after 5 minute sent",
            status_code = status.HTTP_403_FORBIDDEN
    )

class DeleteMessageTimeout(HTTPException):
    def __init__(self):
        super().__init__(
            detail = "can not delete message after 5 minute sent",
            status_code = status.HTTP_403_FORBIDDEN
    )