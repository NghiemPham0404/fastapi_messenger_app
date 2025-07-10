from fastapi import HTTPException

class UploadFileException(HTTPException):
    def __init__(self, status_code, detail = None):
        super().__init__(
            status_code = status_code, 
            detail= f"Unable to upload file : {detail} - statuscode : {status_code}"
        )

class NotImageException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code = 400, 
            detail= f"Invalid image"
        )

class OversizeImageException(HTTPException):
    def __init__(self, max_size):
        super().__init__(
            status_code = 413, 
            detail= f"Image too large. Maximum allowed size is {max_size} MB."
        )

class OversizedFileException(HTTPException):
    def __init__(self, max_size):
        super().__init__(
            status_code = 413, 
            detail= f"File too large. Maximum allowed size is {max_size} MB."
        )