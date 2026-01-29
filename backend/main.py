from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, auth, database

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="CyberGuard DLP API")

# CORS - Allow everything for MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "CyberGuard DLP Backend Running"}

@app.post("/auth/google", response_model=schemas.Token)
def google_login(login_data: schemas.GoogleLogin, db: Session = Depends(database.get_db)):
    google_user = auth.verify_google_token(login_data.token)
    email = google_user.get('email')
    name = google_user.get('name')
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(email=email, full_name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer", "is_paid": user.is_paid}

@app.post("/payment/upgrade", response_model=schemas.UserOut)
def upgrade_user(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    # Simulate payment success
    current_user.is_paid = True
    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/events", response_model=schemas.EventOut)
def create_event(
    event: schemas.EventCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Only allow logging if user is paid? Or allow all but show only to paid?
    # Let's allow logging for all authenticated users.
    db_event = models.Event(**event.dict(), user_id=current_user.id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events", response_model=List[schemas.EventOut])
def read_events(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    return db.query(models.Event).filter(models.Event.user_id == current_user.id).order_by(models.Event.timestamp.desc()).all()
