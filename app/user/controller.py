from typing import Annotated
import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, UploadFile
from sqlalchemy.orm import Session

from .models import UserCreate, UserOut, UserUpdate, UserInDB
from .exceptions import UploadAvatarFail, UserAlreadyExist, UserNotFound
from .service import crud

from ..exceptions import NotAuthorized
from ..response import ListResponse, MessageResponse, ObjectResponse
from ..database import get_mysql_db
from ..group.models import GroupOut
from ..security import bcrypt_context, get_current_user
from ..config import load_cloudinay_config

router = APIRouter(prefix="/users", tags=["User"])

@router.get("/", response_model=ListResponse[UserOut])
async def get_users_endpoint(keyword : Annotated[str, Query()] = "",
                             page : int = 1,
                             db: Session = Depends(get_mysql_db),
                             ):
    """
    Get users
    """
    users_page =  crud.get_users(db, keyword, page)
    return ListResponse(**users_page.model_dump(), results=users_page.items)


@router.post("/", response_model=ObjectResponse[UserOut])
async def create_user_endpoint(user_create: UserCreate, 
                               db: Session = Depends(get_mysql_db)):
    # check if user already exists
    user = crud.find_user_by_email(db = db, 
                                   email = user_create.email)
    if not user:
        # create user
        user_in_db = UserInDB(**user_create.model_dump(), hashed_password = bcrypt_context.hash(user_create.password))
        user =  crud.create(db, user_in_db)
        return ObjectResponse(result=user)
    else:
        # return error if user already exists
        return UserAlreadyExist()

@router.get("/{id}", 
            response_model=ObjectResponse[UserOut])
async def get_user_endpoint(id: Annotated[int, Path()], 
                            db: Session = Depends(get_mysql_db)):
    """
    Get user by id
    """
    user = crud.get_one(db, crud._model.id == id)
    if user is None:
        raise UserNotFound()
    return ObjectResponse(result=user)
    

@router.put("/{id}", 
            response_model=ObjectResponse[UserOut])
async def update_user_endpoint(id: Annotated[int, Path()], 
                               user_update: UserUpdate, 
                               db: Session = Depends(get_mysql_db)):
    """"
    Update user by id
    """
    # check if user exists in db
    user = crud.get_one(db, crud._model.id == id)
    if user is None:
        raise UserNotFound()
    # update user
    user_in_db = UserInDB(**user_update.model_dump(), hashed_password = bcrypt_context.hash(user_update.password))
    user =  crud.update(db, user, user_in_db)
    return ObjectResponse(result=user)

@router.delete("/{id}", response_model=MessageResponse)
async def delete_user_endpoint(id: Annotated[int, Path()],
                               db: Session = Depends(get_mysql_db)):
    """
    Delete user by id
    """
    # check if user exists in db
    user = crud.get_one(db, crud._model.id == id)
    if user is None:
        raise UserNotFound()
    # delete user
    crud.delete(db, user)
    return MessageResponse(message = "User deleted sucessfully")

@router.get("/{id}/groups", response_model=ListResponse[GroupOut])
async def get_user_groups(id: int,
                                db: Session = Depends(get_mysql_db), 
                                user: UserOut = Depends(get_current_user),
                                page: int = 1,
                                ):
    """
    Get all groups that a user have joined
    """
    if id != user.id:
        raise NotAuthorized()
    group_page =  crud.get_user_groups(db, user.id, page)
    return ListResponse(**group_page .model_dump(), results= group_page .items)

@router.put("/{id}/avatar",
            response_model=ObjectResponse[UserOut])
def update_user_avatar_endpoint( 
                           avatar: Annotated[UploadFile, File(max=1024*5)],
                           user: UserInDB = Depends(get_current_user), 
                           db: Session = Depends(get_mysql_db)):
    """
    Update user avatar by id
    """
    
    # check if user exists in db
    user = crud.get_one(db, crud._model.id == user.id)
    if user is None:
        raise UserNotFound()
    # update user avatar
    # upload image to cloudinary
    load_cloudinay_config()
    upload_result = cloudinary.uploader.upload(
        avatar.file,
        use_filename = True,
        resource_type="image",
        filename=avatar.filename,
        folder="avatar",
    )
    if upload_result.get("secure_url") is None:
        raise UploadAvatarFail()
    else:
        url = upload_result.get("url")
        filename = url.split("/")[-1]
        user = crud.update(db, user, UserInDB(avatar=filename))
        return ObjectResponse(result= user)