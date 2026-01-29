from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import models, schemas, auth, database

# Create tables
models.Base.metadata.create_all(bind=database.engine)

# Auto-migrate: Add missing columns if they don't exist
try:
    with database.engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR;"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR;"))
        conn.commit()
        print("Schema migration completed successfully.")
except Exception as e:
    print(f"Migration warning (can be ignored if columns exist): {e}")

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

from fastapi.responses import HTMLResponse

@app.get("/auth/google_login_simulation", response_class=HTMLResponse)
def google_login_simulation(callback_port: int):
    """
    Simulates a Google Login page for demonstration.
    In production, this would redirect to https://accounts.google.com/o/oauth2/v2/auth...
    """
    return f"""
    <html>
        <body style="font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5;">
            <div style="background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; max-width: 400px;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" width="60" style="margin-bottom: 20px;">
                <h2 style="color: #202124; margin-bottom: 10px;">Sign in with Google</h2>
                <p style="color: #5f6368; margin-bottom: 30px;">Choose an account to continue to CyberGuard</p>
                
                <div style="text-align: left;">
                    <div style="padding: 10px; border: 1px solid #dadce0; border-radius: 4px; margin-bottom: 10px; cursor: pointer; display: flex; align-items: center;" onclick="login('user@example.com', 'Demo User')">
                        <div style="width: 30px; height: 30px; background: #e8f0fe; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #1a73e8; font-weight: bold; margin-right: 10px;">D</div>
                        <div>
                            <div style="font-weight: 500; color: #3c4043;">Demo User</div>
                            <div style="font-size: 12px; color: #5f6368;">user@example.com</div>
                        </div>
                    </div>
                    
                    <div style="padding: 10px; border: 1px solid #dadce0; border-radius: 4px; margin-bottom: 10px; cursor: pointer; display: flex; align-items: center;" onclick="login('shubham@gmail.com', 'Shubham')">
                        <div style="width: 30px; height: 30px; background: #ceead6; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #137333; font-weight: bold; margin-right: 10px;">S</div>
                        <div>
                            <div style="font-weight: 500; color: #3c4043;">Shubham</div>
                            <div style="font-size: 12px; color: #5f6368;">shubham@gmail.com</div>
                        </div>
                    </div>
                </div>

                <script>
                    async function login(email, name) {
                        // Create user in backend via API
                        const response = await fetch('/auth/google_callback_simulation', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({email, name})
                        });
                        const data = await response.json();
                        
                        // Redirect back to localhost agent
                        window.location.href = `http://localhost:{callback_port}/?token=${{data.access_token}}`;
                    }
                </script>
            </div>
        </body>
    </html>
    """

@app.post("/auth/google_callback_simulation")
def google_callback_simulation(data: dict, db: Session = Depends(database.get_db)):
    email = data.get('email')
    name = data.get('name')
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(email=email, full_name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token}

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
