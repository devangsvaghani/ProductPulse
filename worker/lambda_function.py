import json
import boto3
import os
import urllib.parse
from worker import process_feedback_file
from database import SessionLocal, engine
from models import Base, Upload, AnalysisResult

s3_client = boto3.client("s3")

# Stores the analysis results to the database
def save_results_to_db(results: list, upload_id: int, db_session):
    try:
        for res in results:
            db_result = AnalysisResult(
                upload_id=upload_id,
                topic=res.get("top_words"),
                summary=res.get("ai_summary"),
                sentiment_score=res.get("avg_sentiment"),
                review_count=res.get("review_count"),
                sentiment_details=res.get("sentiment_dict")
            )
            db_session.add(db_result)
        db_session.commit()
        print(f"Successfully saved {len(results)} analysis results to the database.")
    except Exception as e:
        db_session.rollback()
        print(f"Error saving to database: {e}")
        raise

# Entry Point
def lambda_handler(event, context):

    print("Lambda function triggered by SQS event.")

    Base.metadata.create_all(bind=engine)
    
    for record in event['Records']:
        sqs_body_str = record['body']
        s3_event_data = json.loads(sqs_body_str)
        s3_record = s3_event_data['Records'][0]
        bucket_name = s3_record['s3']['bucket']['name']
        file_key = urllib.parse.unquote_plus(s3_record['s3']['object']['key'])

        actual_filename = file_key
        try:
            user_id_str, actual_filename = file_key.split('/', 1)
            user_id = int(user_id_str)
        except (ValueError, IndexError):
            print(f"ERROR: Could not parse user_id from S3 key: {file_key}")
            continue

        print(f"Processing file: {file_key} from bucket: {bucket_name}")

        download_path = f'/tmp/{os.path.basename(file_key)}'
        s3_client.download_file(bucket_name, file_key, download_path)
        
        db = SessionLocal()
        upload_record = None
        try:
            upload_record = Upload(filename=actual_filename, status='processing', user_id=user_id)
            db.add(upload_record)
            db.commit()
            db.refresh(upload_record)
            print(f"Created new upload record with ID: {upload_record.id}")

            analysis_results = process_feedback_file(download_path)
            
            if analysis_results:
                save_results_to_db(analysis_results, upload_record.id, db)
                upload_record.status = 'completed'
            else:
                upload_record.status = 'failed'
            
            db.commit()

        except Exception as e:
            db.rollback()
            print(f"A top-level error occurred: {e}")
            if upload_record:
                upload_record.status = 'failed'
                db.commit()
            raise
        
        finally:
            db.close()

    return {'statusCode': 200, 'body': json.dumps('Processing complete!')}