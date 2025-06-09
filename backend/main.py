from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# --- Setup ---
# Load all the environment variables from the .env file
load_dotenv()
app = FastAPI(title="ProductPulse API")

# Configure the Boto3 S3 client.
# It will automatically use the credentials loaded from your .env file.
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
S3_BUCKET = os.getenv("S3_BUCKET_NAME")


# --- API Request/Response Models ---
# This defines the structure of the incoming request JSON
class UploadRequest(BaseModel):
    filename: str
    filetype: str # e.g., 'text/csv'


# --- API Endpoints ---
@app.get("/")
def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the ProductPulse API!"}


@app.post("/upload-url")
def get_presigned_upload_url(request: UploadRequest):
    """
    Generates a secure, temporary URL for a client to upload a file
    directly to our S3 bucket.
    """
    # Ensure the S3 bucket name is configured in the .env file
    if not S3_BUCKET:
        raise HTTPException(status_code=500, detail="S3_BUCKET_NAME is not configured.")

    try:
        # Generate the presigned POST URL. It will be valid for 10 minutes.
        presigned_post = s3_client.generate_presigned_post(
            Bucket=S3_BUCKET,
            Key=request.filename,  # The name the file will have once uploaded to S3
            Fields={"acl": "private", "Content-Type": request.filetype},
            Conditions=[
                {"acl": "private"},
                {"Content-Type": request.filetype}
            ],
            ExpiresIn=600  # URL is valid for 600 seconds (10 minutes)
        )
        
        print(f"Successfully generated presigned URL for {request.filename}")
        return presigned_post

    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        raise HTTPException(status_code=400, detail=f"Could not generate upload URL: {e}")