from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.user_base import UserCreate, UserOut, UserUpdate, UserInDB
from crud.user import crud
from security import bcrypt_context, get_current_user


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut)
async def create_user_endpoint(user_create: UserCreate, db: Session = Depends(get_db)):
    user = crud.find_user_by_email(db = db, email = user_create.email)
    if not user:
        user_in_db = UserInDB(**user_create.model_dump(), hashed_password = bcrypt_context.hash(user_create.password))
        return crud.create(db, user_in_db)
    else:
        return HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"The user with this {user_create.email} already exists \in the system")

@router.get("/", response_model=list[UserOut])
async def get_users_endpoint(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return crud.get_many(db = db, skip=skip, limit=limit)

@router.get("/search", response_model=list[UserOut])
async def get_users_endpoint(query : str,skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return crud.get_many(db, crud._model.name.like(f"%{query}%") , skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserOut)
async def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_one(db, crud._model.id == user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
    
@router.put("/{user_id}", response_model=UserOut)
async def update_user_endpoint(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = crud.get_one(db, crud._model.id == user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_in_db = UserInDB(**user_update.model_dump(), hashed_password = bcrypt_context.hash(user_update.password))
    return crud.update(db, user, user_in_db)

@router.delete("/{user_id}")
async def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_one(db, crud._model.id == user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete(db, user)
    return {"message": "User deleted"}
