import re
import uuid
from fastapi import HTTPException
from pydantic import BaseModel, field_validator, EmailStr, constr, Field
from typing import Optional, List
from datetime import datetime
from db.models.users import UserRole

class TunedModel(BaseModel):
    class Config:
        from_attributes = True

class UserRead(TunedModel):
    user_id: int
    name: str
    surname: str
    username: str
    photo: str = ""
    header_photo: str = ""
    email: EmailStr
    about: str = ""
    location: str = ""
    age: int = 0
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    frame_photo: Optional[str] = None
    is_premium: bool = False
    premium_until: Optional[datetime] = None
    money: float = 0.0
    level: int = 1
    title: str = "Новичок"
    role: UserRole = UserRole.USER

class UserReadLimited(TunedModel):
    user_id: int
    username: str
    photo: str
    header_photo: str
    about: str
    location: str
    age: int
    created_at: datetime
    is_premium: bool
    level: int
    title: str

class UserBase(BaseModel):
    username: str
    email: EmailStr
    name: str
    surname: str

    @field_validator("name", "surname", mode="before")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Имя и фамилия не могут быть пустыми")
        return v.strip()

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    user_id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    photo: str
    header_photo: str
    frame_photo: Optional[str] = None
    about: str
    location: str
    age: int
    is_premium: bool
    premium_until: Optional[datetime]
    money: float
    level: int
    title: str

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    pass

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    photo: Optional[str] = None
    header_photo: Optional[str] = None
    frame_photo: Optional[str] = None
    about: Optional[str] = None
    location: Optional[str] = None
    age: Optional[int] = None

    class Config:
        extra = "forbid"
        validate_assignment = True

class UserDeleteResponse(BaseModel):
    user_id: int

class UserUpdateResponse(BaseModel):
    updated_user_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class UserRoleUpdate(BaseModel):
    role: UserRole

class UserRoleUpdateResponse(BaseModel):
    user_id: int
    role: UserRole

class MoneyTransactionRequest(BaseModel):
    amount: float

class MoneyTransactionResponse(BaseModel):
    success: bool
    new_balance: float
    message: str

class LevelUpdateRequest(BaseModel):
    new_level: int = Field(..., gt=0, description="Новый уровень пользователя")

class LevelUpdateResponse(BaseModel):
    new_level: int
    new_title: str
    message: str

class MoneyAddRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Количество монет для добавления")

class MoneyAddResponse(BaseModel):
    success: bool
    message: str
    new_balance: float

