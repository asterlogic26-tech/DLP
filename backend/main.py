from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth, database

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

@app.post("/auth/signup", response_model=schemas.Token)
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    access_token = auth.create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer", "is_paid": db_user.is_paid}

@app.post("/auth/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not user.hashed_password:
        # If user was created via Google Login or Simple Login, they don't have a password
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please login with Google or reset password")
        
    if not auth.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
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
