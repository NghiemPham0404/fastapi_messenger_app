
from typing import Annotated
from fastapi import APIRouter,Depends, File, UploadFile

from .exception import NotImageException, OversizeImageException, OversizedFileException, UploadFileException
from .models import FileUploadOut, ImageUploadOut
from .service import MediaFileService

from ..response import ObjectResponse
from ..user.exceptions import UserNotFound
from ..security import get_current_user

router = APIRouter(tags=["media_file"])

service = MediaFileService()

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}


MAX_IMAGE_MB_SIZE = 2
MAX_IMAGE_SIZE = MAX_IMAGE_MB_SIZE * 1024 * 1024


MAX_FILE_MB_SIZE = 10
MAX_FILE_SIZE = MAX_FILE_MB_SIZE * 1024 * 1024


def validate_image_type(image : UploadFile):
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise NotImageException()
    

def validate_image_size(image :  UploadFile):
    contents = image.file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise OversizeImageException(max_size=MAX_IMAGE_SIZE)
    image.file.seek(0)
    
def validate_file_size(file : UploadFile):
    contents = file.file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise OversizedFileException(max_size=MAX_FILE_SIZE)
    file.file.seek(0)


@router.post("/image", response_model = ObjectResponse[ImageUploadOut])
def send_image_to_server(image : Annotated[UploadFile, File()],
                         user = Depends(get_current_user),):
    
    # validate current user
    if user is None:
        return UserNotFound()
    
    # validate file sized
    validate_image_size(image)

    # validate image type
    validate_image_type(image)
    
    upload_result = service.uploadImage(image)
    if upload_result.get("secure_url") is not None:
        uploaded_image = ImageUploadOut(
            image_url = upload_result.get("secure_url"),
            original_filename=upload_result.get("original_filename"),
            display_name=upload_result.get("display_name"),                   
        )
        return ObjectResponse(result =  uploaded_image)
    else:
        raise UploadFileException(status_code=400, detail = upload_result.get("error").get("message"))
    

@router.post("/file", response_model = ObjectResponse[FileUploadOut])
def send_file_to_server(file : Annotated[UploadFile, File()],
                         user = Depends(get_current_user),):
    
    # validate current user
    if user is None:
        return UserNotFound()
    
    # validate file sized
    validate_file_size(file)
    
    upload_result = service.uploadFile(file)
    if upload_result.get("secure_url") is not None:
        uploaded_file = FileUploadOut(
            file_url = upload_result.get("secure_url"),
            original_filename=upload_result.get("original_filename"),
            display_name=upload_result.get("display_name"),                   
        )
        return ObjectResponse(result= uploaded_file)
    else:
        raise UploadFileException(status_code=400, detail = upload_result.get("error").get("message"))


# @router.post("/images")
# def send_images_to_server(user = Depends(get_current_user),
#                           images = list[UploadFile]):
    
#     if user is None:
#         return UserNotFound()
    

#     upload_results =  service.uploadMultiImages()
#     uploaded_images = []
#     for upload_result in upload_results:
#         uploaded_image = ImageUploadOut(
#             image_url = upload_result.get("secure_url"),
#             original_filename=upload_result.get("original_filename"),
#             display_name=upload_result.get("display_name"),                   
#         )
#         uploaded_images.append(uploaded_image)
#     if len (uploaded_images) == 0 :
#         raise UploadFileException()
#     else:
#         return uploaded_images