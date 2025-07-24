from typing import Annotated
import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, UploadFile
from sqlalchemy.orm import Session

from .models import UserCreate, UserOut, UserUpdate, UserInDB, UserOutExtend
from .exceptions import UploadAvatarFail, UserAlreadyExist, UserNotFound
from .service import crud

from ..exceptions import NotAuthorized
from ..response import ListResponse, MessageResponse, ObjectResponse
from ..database import get_mysql_db
from ..group.models import GroupOut
from ..security import bcrypt_context, get_current_user
from ..config import load_cloudinay_config

router = APIRouter(prefix="/users", tags=["User"])

@router.get("/", response_model=ListResponse[UserOutExtend])
async def get_users_endpoint(keyword : Annotated[str, Query()] = "",
                             page : int = 1,
                             limit : int = 20,
                             db: Session = Depends(get_mysql_db),
                             user: UserOut = Depends(get_current_user),
                             ):
    """
    Get users
    """
    return crud.get_users(db, keyword, user.id, page, limit)


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
        raise UserAlreadyExist()

@router.get("/{id}", 
            response_model=ObjectResponse[UserOutExtend])
async def get_user_endpoint(id: Annotated[int, Path()], 
                            db: Session = Depends(get_mysql_db),
                            current_user: UserOut = Depends(get_current_user),
                            ):
    """
    Get user by id
    """
    user = crud.get_one(db, crud._model.id == id)

    if user is None:
        raise UserNotFound()
    
    user_extend = crud.convert_user_to_user_extend(db, user, current_user.id)
    return ObjectResponse(result=user_extend)
    

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
    user_in_db = UserInDB(**user_update.model_dump(exclude_defaults=True, 
                                                   exclude_unset=True))
    if user_update.password:
        user_in_db.hashed_password = bcrypt_context.hash(user_update.password)
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
                                status : Annotated[int, Query()] = 1,
                                page: int = 1,
                                ):
    """
    Get all groups of a user
    
    params:
    - status:
        - 1 : joined group
        - 0 : being invited to join
        - 2 : requested to join and waiting to be accepted by groupd-admin 
    """
    if id != user.id:
        raise NotAuthorized()
    group_page =  crud.get_user_groups(db, user.id, status, page)
    return ListResponse(**group_page .model_dump(), results= group_page .items)

@router.put("/{id}/avatar",
            response_model=ObjectResponse[UserOut])
def update_user_avatar_endpoint(id : Annotated[int, Path()], 
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