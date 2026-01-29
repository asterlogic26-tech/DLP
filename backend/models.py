from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_paid = Column(Boolean, default=False) # For the payment flow
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    events = relationship("Event", back_populates="owner")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String) # "LEAK_ATTEMPT", "SPAM", "ADULT_CONTENT"
    description = Column(String)
    url = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    action_taken = Column(String) # "BLOCKED", "ALLOWED"

    owner = relationship("User", back_populates="events")
