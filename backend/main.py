from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
import razorpay
import json

# Fix for running as script
try:
    from . import models, schemas, auth, database
except ImportError:
    import models, schemas, auth, database

# Create tables if they don't exist
models.Base.metadata.create_all(bind=database.engine)

# Configure root_path for Vercel deployment
root_path = "/api" if os.getenv("VERCEL") else ""
app = FastAPI(root_path=root_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Razorpay Client
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY", "YOUR_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_SECRET", "YOUR_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "YOUR_WEBHOOK_SECRET")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

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
    sub = db.query(models.Subscription).filter(
        models.Subscription.user_id == current_user["id"]
    ).first()
    
    is_active = sub is not None and sub.status == "active"
    return {"active": is_active}

@app.post("/subscription/create")
def create_subscription(
    sub_in: schemas.SubscriptionCreate,
    current_user: dict = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    plan_id = os.getenv("RAZORPAY_B2C_PLAN") if sub_in.plan == "B2C" else os.getenv("RAZORPAY_B2B_PLAN")
    if not plan_id:
        # Fallback for testing/demo
        plan_id = "plan_test_id"

    try:
        subscription = razorpay_client.subscription.create({
            "plan_id": plan_id,
            "customer_notify": 1,
            "total_count": 120 # 10 years
        })
        
        db_sub = models.Subscription(
            user_id=current_user["id"],
            razorpay_subscription_id=subscription['id'],
            plan=sub_in.plan,
            status="created"
        )
        db.add(db_sub)
        db.commit()
        
        return subscription
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(database.get_db)):
    body = await request.body()
    signature = request.headers.get("x-razorpay-signature")
    
    try:
        razorpay_client.utility.verify_webhook_signature(
            body.decode(), signature, RAZORPAY_WEBHOOK_SECRET
        )
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    data = await request.json()
    event = data.get("event")
    
    # Payload structure varies, usually payload.subscription.entity
    try:
        payload = data.get("payload", {})
        sub_entity = payload.get("subscription", {}).get("entity", {})
        sub_id = sub_entity.get("id")
        
        if sub_id:
            sub = db.query(models.Subscription).filter(
                models.Subscription.razorpay_subscription_id == sub_id
            ).first()
            
            if sub:
                if event == "subscription.activated":
                    sub.status = "active"
                elif event == "subscription.cancelled":
                    sub.status = "cancelled"
                
                db.commit()
    except Exception as e:
        print(f"Webhook processing error: {e}")

    return {"status": "ok"}


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
