import json
import boto3
import os
from worker import process_feedback_file
from database import SessionLocal, engine
from models import Base, Upload, AnalysisResult

# Create an S3 client to download the file from the trigger event
s3_client = boto3.client("s3")

def save_results_to_db(results: list, upload_id: int):
    """Connects to the DB and saves the analysis results."""
    db = SessionLocal()
    try:
        for res in results:
            db_result = AnalysisResult(
                upload_id=upload_id,
                topic=res.get("top_words"),
                summary=res.get("ai_summary"),
                sentiment=str(res.get("sentiment")), # Store sentiment dict as string
                sentiment_score=res.get("avg_sentiment"),
                roadmap_json=None # We can add this later if needed
            )
            db.add(db_result)
        db.commit()
        print(f"Successfully saved {len(results)} analysis results to the database.")
    except Exception as e:
        db.rollback()
        print(f"Error saving to database: {e}")
        raise
    finally:
        db.close()

def lambda_handler(event, context):
    """
    This function is the entry point for the AWS Lambda execution.
    It downloads the file from S3, processes it, and saves results to RDS.
    """
    print("Lambda function triggered by SQS event.")
    
    # Ensure our database tables exist
    Base.metadata.create_all(bind=engine)
    
    for record in event['Records']:
        s3_event = json.loads(record['body'])
        bucket_name = s3_event['Records'][0]['s3']['bucket']['name']
        file_key = s3_event['Records'][0]['s3']['object']['key']
        
        print(f"Processing file: {file_key} from bucket: {bucket_name}")
        
        # Download the file from S3 to Lambda's temporary storage
        download_path = f'/tmp/{file_key.split("/")[-1]}'
        s3_client.download_file(bucket_name, file_key, download_path)
        
        db = SessionLocal()
        try:
            # Create a record for the upload itself
            new_upload = Upload(filename=file_key, status='processing')
            db.add(new_upload)
            db.commit()
            db.refresh(new_upload)
            upload_id = new_upload.id
            print(f"Created new upload record with ID: {upload_id}")

            # Run our AI pipeline on the downloaded file
            analysis_results = process_feedback_file(download_path)
            
            if analysis_results:
                # Save the results to the database
                save_results_to_db(analysis_results, upload_id)
                # Update the upload status to 'completed'
                new_upload.status = 'completed'
            else:
                new_upload.status = 'failed'
                
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"A top-level error occurred: {e}")
            # Try to mark the job as failed if possible
            if 'new_upload' in locals():
                new_upload.status = 'failed'
                db.commit()
            raise
        finally:
            db.close()

    return {'statusCode': 200, 'body': json.dumps('Processing complete!')}