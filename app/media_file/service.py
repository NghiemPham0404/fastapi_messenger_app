
import cloudinary
from fastapi import UploadFile
from ..config import load_cloudinay_config

# resource_type : raw, image, video
# 
#

class MediaFileService():

    def __init__(self):
        load_cloudinay_config()
    
    def uploadFile(self, file : UploadFile):
        upload_result = cloudinary.uploader.upload(
            file.file,
            use_filename = True,
            filename_override = file.filename,
            resource_type="raw",
            folder="files",
        )
        return upload_result

        
    def uploadImage(self, image : UploadFile):
        upload_result = cloudinary.uploader.upload(
            image.file,
            use_filename = True,
            resource_type="image",
            filename_override = image.filename,
            folder="images",
        )
        return upload_result

    # def uploadMultiImages(images : list[UploadFile]):
    #     successful_result = []
    #     for image in images:
    #         upload_result = cloudinary.uploader.upload(
    #             image.file,
    #             use_filename = True,
    #             resource_type="image",
    #             folder="images",
    #         )
    #         successful_result.append(upload_result)
    #     return successful_result



        
    