import boto3
from botocore.client import Config
from datetime import datetime
from app.config import get_settings

settings = get_settings()

class R2Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.r2_endpoint,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        self.bucket_name = settings.r2_bucket_name
    
    def upload_lesson(self, lesson_slug: str, file_content: bytes) -> str:
        timestamp = int(datetime.now().timestamp() * 1000)
        file_key = f"lessons/{lesson_slug}/{timestamp}.mdx"
        
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=file_key,
            Body=file_content,
            ContentType='text/markdown'
        )
        
        return file_key
    
    def get_lesson_content(self, file_key: str) -> str:
        response = self.s3_client.get_object(
            Bucket=self.bucket_name,
            Key=file_key
        )
        return response['Body'].read().decode('utf-8')
    
    def delete_lesson(self, file_key: str) -> bool:
        try:
            self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
r2_service = R2Service()