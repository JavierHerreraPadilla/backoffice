# from random import randint
# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
# from app import USERS
# from pydantic import BaseModel, EmailStr
# import oauth2
# import utils


# router = APIRouter(
#     tags=["authentication"]
# )

# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str

# class User(BaseModel):
#     user_id: UserLogin
