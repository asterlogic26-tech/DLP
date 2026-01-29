from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
import json

# Fix for running as script
try:
    from . import models, schemas, auth, database
except ImportError:
    import models, schemas, auth, database

# Create tables if they don't exist
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Payments temporarily disabled; Razorpay removed

@app.post("/auth/login", response_model=schemas.Token)
def login(user_in: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if not user or not auth.verify_password(user_in.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    access_token = auth.create_access_token(
        data={"id": str(user.id), "org_id": str(user.org_id)}
    )
    return {"token": access_token}

@app.post("/auth/google", response_model=schemas.Token)
def google_login(login_data: schemas.GoogleLogin, db: Session = Depends(database.get_db)):
    try:
        google_user = auth.verify_google_token(login_data.token)
    except ValueError as e:
         # Return the specific verification error (e.g. "Audience mismatch", "Token expired")
         raise HTTPException(status_code=400, detail=f"Invalid Google Token: {str(e)}")
    
    email = google_user['email']
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(
            email=email,
            password="",
            org_id=uuid.uuid4()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = auth.create_access_token(
        data={"id": str(user.id), "org_id": str(user.org_id)}
    )
    return {"token": access_token}

@app.get("/auth/status", response_model=schemas.SubscriptionStatus)
def get_status(
    current_user: dict = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Temporarily consider all users active until payments are re-enabled
    return {"active": True}

# Subscription creation removed

# Razorpay webhook removed


@app.post("/events", response_model=dict)
def create_event(
    event: schemas.EventCreate,
    current_user: dict = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    db_event = models.Event(
        user_id=current_user["id"],
        org_id=current_user["org_id"],
        **event.dict()
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return {"status": "ok"}

@app.get("/events", response_model=List[schemas.EventOut])
def read_events(
    current_user: dict = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    events = db.query(models.Event).filter(
        models.Event.org_id == current_user["org_id"]
    ).order_by(models.Event.created_at.desc()).limit(50).all()
    return events

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=3000, reload=True)
