from typing import List
import boto3
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.config import settings
from database import models
from database.session import get_db
from schemas import analysis as schemas
from auth import get_current_user

router = APIRouter()

@router.post("/presigned-url", response_model=schemas.PresignedUrlResponse)
def create_presigned_url(filename: str, current_user: models.User = Depends(get_current_user)):
    # Generates a presigned URL for uploading a file to S3
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    try:

        s3_key = f"{current_user.id}/{filename}"

        response = s3_client.generate_presigned_post(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            Fields={"acl": "private", "Content-Type": "text/csv"},
            Conditions=[
                {"acl": "private"},
                {"Content-Type": "text/csv"}
            ],
            ExpiresIn=3600  # URL expires in 1 hour
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not generate presigned URL: {e}")

@router.get("/", response_model=List[schemas.UploadInfo])
def get_all_uploads(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    all_uploads = db.query(models.Upload).filter(models.Upload.user_id == current_user.id).order_by(models.Upload.created_at.desc()).all()
    return all_uploads

@router.get("/{upload_id}", response_model=schemas.UploadResponse)
def get_upload_results(upload_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    upload = db.query(models.Upload).filter(models.Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    if upload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    return upload