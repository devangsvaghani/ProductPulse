from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from database.session import get_db
from database import models
from schemas import admin as admin_schemas
from schemas.auth import User as UserSchema 
from auth import get_current_admin_user, get_password_hash

router = APIRouter()

PROTECTED = [Depends(get_current_admin_user)]

# fetch all users
@router.get("/users", response_model=List[UserSchema], dependencies=PROTECTED)
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# create a new user
@router.post("/users", response_model=UserSchema, status_code=status.HTTP_201_CREATED, dependencies=PROTECTED)
def create_new_user(user: admin_schemas.UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        nickname=user.nickname,
        is_admin=user.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# update user having user_id
@router.put("/users/{user_id}", response_model=UserSchema, dependencies=PROTECTED)
def update_existing_user(user_id: int, user_update: admin_schemas.UserUpdate, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.commit()
    db.refresh(db_user)
    return db_user

# delete user having user_id
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=PROTECTED)
def delete_existing_user(user_id: int, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return

# get all analytics data
@router.get("/analytics", response_model=admin_schemas.AnalyticsData, dependencies=PROTECTED)
def get_platform_analytics(db: Session = Depends(get_db)):
    
    total_users = db.query(models.User).count()
    total_uploads = db.query(models.Upload).count()
    total_analysis_results = db.query(models.AnalysisResult).count()
    
    status_counts = db.query(
        models.Upload.status, 
        func.count(models.Upload.id)
    ).group_by(models.Upload.status).all()
    
    uploads_by_status = {status: count for status, count in status_counts}
    
    return {
        "total_users": total_users,
        "total_uploads": total_uploads,
        "total_analysis_results": total_analysis_results,
        "uploads_by_status": uploads_by_status
    }