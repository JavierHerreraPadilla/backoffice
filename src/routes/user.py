from random import randint
from fastapi import Depends, status, HTTPException, APIRouter
from ..utils import USERS
from pydantic import BaseModel, EmailStr
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import oauth2
from .. import utils

router = APIRouter(
    tags=["user_creation"]
)

class UserRegister(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    user_id: int
    email: EmailStr


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=User)
async def reg(user: UserRegister):
    # hash password
    user.password = utils.hash_pass(user.password)
    user_id = randint(0, 9999)
    USERS[user_id] = user
    print(USERS)
    return {"user_id": user_id, "email": user.email}


@router.post("/login", response_model=oauth2.Token)
async def login(user_login: OAuth2PasswordRequestForm = Depends()):
    # check password
    print(user_login.username, user_login.password)
    users = [(user_id, user) for user_id, user in USERS.items() if user.email == user_login.username]
    
    print(users)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    user_info = users[0]
    user = user_info[1]
    user_password = user.password
    user_id = user_info[0]
    print("user pass", user_password)
    if not utils.verify_pass(user_login.password, user_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid credentials")
    # create token
    access_token = oauth2.create_access_token(data={"user_id": user_id, "user_email": user.email})
    # return token
    return {"token": access_token, "token_type": "bearer"}