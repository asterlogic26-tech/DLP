from sqlalchemy import Column, String, ForeignKey, DateTime, func, Uuid
import uuid
try:
    from .database import Base
except ImportError:
    from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    org_id = Column(Uuid(as_uuid=True))

class Event(Base):
    __tablename__ = "events"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True))
    org_id = Column(Uuid(as_uuid=True))
    data_type = Column(String)
    action = Column(String)
    domain = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True))
    razorpay_subscription_id = Column(String, unique=True)
    plan = Column(String)
    status = Column(String)
    current_period_end = Column(DateTime(timezone=True))
