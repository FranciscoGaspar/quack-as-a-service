"""
S3 Uploader utility for uploading images to AWS S3.
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional
from datetime import datetime
import mimetypes
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def upload_image_to_s3(file_path: str) -> Optional[str]:
    """
    Upload an image file directly to S3. Handles everything internally.

    This function:
    1. Loads AWS credentials from environment variables
    2. Creates S3 client
    3. Validates the image file
    4. Uploads with randomly generated name and folder
    5. Returns the public S3 URL

    Args:
        file_path (str): Path to the local image file

    Returns:
        str: S3 URL of the uploaded file if successful, None otherwise
    """
    try:
        # Load environment variables
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        bucket_name = os.getenv('S3_BUCKET_NAME')
        region = os.getenv('AWS_REGION', 'us-east-1')

        # Validate environment variables
        if not all([aws_access_key_id, aws_secret_access_key, bucket_name]):
            print(
                "Error: Missing required AWS environment variables. Please check your .env file.")
            return None

        # Verify file exists
        if not os.path.isfile(file_path):
            print(f"Error: File '{file_path}' not found.")
            return None

        # Check if it's an image file
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type or not mime_type.startswith('image/'):
            print(f"Error: '{file_path}' is not a valid image file.")
            return None

        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region
        )

        # Generate random object name and folder
        file_extension = os.path.splitext(file_path)[1]
        random_uuid = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        object_name = f"{random_uuid}_{timestamp}{file_extension}"

        # Create S3 key
        s3_key = f"{object_name}"

        # Upload the file
        extra_args = {
            'ContentType': mime_type,
            'ContentDisposition': 'inline'
        }

        s3_client.upload_file(
            file_path,
            bucket_name,
            s3_key,
            ExtraArgs=extra_args
        )

        # Generate the S3 URL
        s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"

        print(f"File uploaded successfully to: {s3_url}")
        return s3_url

    except NoCredentialsError:
        print("Error: AWS credentials not found.")
        return None
    except ClientError as e:
        print(f"Error uploading file: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
