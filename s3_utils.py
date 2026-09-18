import boto3
from datetime import datetime

s3 = boto3.client(
    's3',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY',
    region_name='us-east-1'
)

BUCKET_NAME = 'dyslexia-storage-yourname'

# Upload with versioning
def upload_file(file, username):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version = f"v{timestamp}"
    key = f"{username}/{file.filename}/{version}"
    
    # Upload to S3
    s3.upload_fileobj(file.file, BUCKET_NAME, key)
    
    # Create backup (copy to backup folder)
    backup_key = f"backup/{key}"
    s3.copy_object(
        Bucket=BUCKET_NAME,
        CopySource={'Bucket': BUCKET_NAME, 'Key': key},
        Key=backup_key
    )
    
    return {"key": key, "version": version, "backup": backup_key}

# Download
def download_file(key):
    response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    return response['Body'].read()

# List all versions
def list_versions(username, filename):
    response = s3.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=f"{username}/{filename}/"
    )
    return [obj['Key'] for obj in response.get('Contents', [])]