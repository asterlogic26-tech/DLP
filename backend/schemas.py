from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: int
    is_paid: bool
    class Config:
        orm_mode = True

class EventBase(BaseModel):
    event_type: str
    description: str
    url: str
    action_taken: str

class EventCreate(EventBase):
    pass

class EventOut(EventBase):
    id: int
    timestamp: datetime
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    is_paid: bool

class GoogleLogin(BaseModel):
    token: str
