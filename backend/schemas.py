from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

class UserLogin(BaseModel):
    email: str
    password: str

class GoogleLogin(BaseModel):
    token: str

class Token(BaseModel):
    token: str

class EventCreate(BaseModel):
    data_type: str
    action: str
    domain: str

class EventOut(EventCreate):
    id: uuid.UUID
    created_at: datetime
    class Config:
        orm_mode = True

class SubscriptionCreate(BaseModel):
    plan: str

class SubscriptionStatus(BaseModel):
    active: bool
