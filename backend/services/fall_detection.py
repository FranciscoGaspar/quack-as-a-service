"""
Fall Detection Service using YOLO

This service handles video processing for fall detection using YOLO model.
It processes uploaded video files, runs them through fall detection algorithms,
uploads results to S3, and returns detection results.
"""

from utils.s3_uploader import upload_image_bytes_to_s3
import os
import tempfile
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from dotenv import load_dotenv
import shutil

# Load environment variables
load_dotenv()

# Optional ML dependencies - import only if available
try:
    from ultralytics import YOLO
    ML_DEPENDENCIES_AVAILABLE = True
    print("✅ YOLO dependencies loaded - fall detection enabled")
except ImportError as e:
    print(
        f"⚠️  YOLO dependencies not available - fall detection disabled: {e}")
    print("💡 To enable fall detection, install: pip install ultralytics")
    ML_DEPENDENCIES_AVAILABLE = False


class FallDetectionService:
    """Service for YOLO-based fall detection video processing."""

    def __init__(self):
        self.model = None
        self.model_path = "./falldetect-11x.pt"
        self.is_initialized = False

    def initialize_model(self):
        """Initialize the YOLO fall detection model."""
        if not ML_DEPENDENCIES_AVAILABLE:
            raise ImportError("YOLO dependencies not available")

        try:
            print("🤖 Loading YOLO fall detection model...")
            if not os.path.exists(self.model_path):
                print(f"⚠️  Model file not found at {self.model_path}")
                print("💡 Make sure falldetect-11x.pt is in the backend directory")
                raise FileNotFoundError(
                    f"Model file not found: {self.model_path}")

            self.model = YOLO(self.model_path)
            self.is_initialized = True
            print("✅ YOLO fall detection model loaded successfully")

        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            raise

    def process_video(self, video_bytes: bytes, filename: str = None, user_id: int = None, location: str = None) -> Dict[str, Any]:
        """
        Process video for fall detection using YOLO.

        Args:
            video_bytes: Raw video bytes
            filename: Original filename
            user_id: Optional user ID
            location: Optional location

        Returns:
            Dictionary with processing results and S3 URLs
        """
        if not self.is_initialized:
            self.initialize_model()

        start_time = time.time()
        print(
            f"🎬 Starting fall detection analysis at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # Save video to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(video_bytes)
                temp_video_path = temp_file.name

            try:
                # Upload original video to S3
                original_video_url = self._upload_video_to_s3(
                    video_bytes, filename, "original")

                # Run YOLO inference on the video
                detection_result = self._analyze_video_with_yolo(
                    temp_video_path, filename)

                # Get processed video path from YOLO output
                processed_video_path = detection_result.get(
                    'output_video_path')
                processed_video_url = None

                # Upload processed video to S3 if it exists
                if processed_video_path and os.path.exists(processed_video_path):
                    with open(processed_video_path, 'rb') as f:
                        processed_video_bytes = f.read()

                    processed_filename = f"processed_{filename}" if filename else "processed_video.mp4"
                    processed_video_url = self._upload_video_to_s3(
                        processed_video_bytes,
                        processed_filename,
                        "processed"
                    )

                    # Clean up the output directory
                    if os.path.exists(processed_video_path):
                        output_dir = os.path.dirname(processed_video_path)
                        if os.path.exists(output_dir):
                            shutil.rmtree(output_dir, ignore_errors=True)

                # Calculate processing time
                processing_time = time.time() - start_time

                # Prepare result
                result = {
                    'detection_result': {
                        'fall_detected': detection_result['fall_detected'],
                        'total_detections': detection_result['total_detections'],
                        'confidence_scores': detection_result['confidence_scores'],
                        'video_duration': detection_result.get('video_duration', 0.0),
                        'processing_time': processing_time,
                        'analysis_timestamp': datetime.now().isoformat(),
                        'model_version': 'falldetect-11x'
                    },
                    'original_video_url': original_video_url,
                    'processed_video_url': processed_video_url,
                    'processing_timestamp': datetime.now().isoformat(),
                    'video_filename': filename,
                    'user_id': user_id,
                    'location': location
                }

                print(
                    f"✅ Fall detection completed in {processing_time:.2f} seconds")
                print(
                    f"   Fall detected: {'YES' if detection_result['fall_detected'] else 'NO'}")
                print(
                    f"   Total detections: {detection_result['total_detections']}")

                return result

            finally:
                # Clean up temporary file
                if os.path.exists(temp_video_path):
                    os.unlink(temp_video_path)

        except Exception as e:
            print(f"❌ Error processing video: {e}")
            raise

    def _analyze_video_with_yolo(self, video_path: str, filename: str = None) -> Dict[str, Any]:
        """
        Analyze video using YOLO model based on your provided code.

        Args:
            video_path: Path to the video file
            filename: Original filename for output naming

        Returns:
            Dictionary with detection results
        """
        try:
            # Create timestamp for output
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Create output directory
            output_base = "./output"
            os.makedirs(output_base, exist_ok=True)

            # Run inference and save the video with detection boxes
            print(f"🔍 Running YOLO inference on video...")
            results = self.model(
                video_path,
                save=True,
                project=output_base,
                name=f"{timestamp}",
                stream=True,
                device='mps' if hasattr(self.model, 'device') else 'cpu',
                half=True
            )

            # Process results and count detections
            detection_count = 0
            confidence_scores = []

            for result in results:
                if result.boxes is not None and len(result.boxes) > 0:
                    detection_count += len(result.boxes)
                    # Extract confidence scores
                    if hasattr(result.boxes, 'conf'):
                        conf_scores = result.boxes.conf.cpu().numpy().tolist()
                        confidence_scores.extend(conf_scores)

            # Determine output video path
            output_video_path = os.path.join(
                output_base, timestamp, video_path.split('/')[-1])

            # Check if output video exists
            if not os.path.exists(output_video_path):
                # Try alternative path structure that YOLO might use
                alt_path = os.path.join(
                    output_base, timestamp, f"{timestamp}.mp4")
                if os.path.exists(alt_path):
                    output_video_path = alt_path
                else:
                    # Look for any .mp4 file in the output directory
                    output_dir = os.path.join(output_base, timestamp)
                    if os.path.exists(output_dir):
                        for file in os.listdir(output_dir):
                            if file.endswith('.mp4'):
                                output_video_path = os.path.join(
                                    output_dir, file)
                                break

            fall_detected = detection_count > 0

            result_data = {
                'fall_detected': fall_detected,
                'total_detections': detection_count,
                'confidence_scores': confidence_scores,
                'output_video_path': output_video_path if os.path.exists(output_video_path) else None,
                'video_duration': 0.0  # Could be calculated if needed
            }

            print(f"📊 YOLO Analysis Results:")
            print(f"   Fall detected: {'YES' if fall_detected else 'NO'}")
            print(f"   Total detections: {detection_count}")
            print(f"   Output video: {output_video_path}")

            return result_data

        except Exception as e:
            print(f"❌ Error during YOLO analysis: {e}")
            raise

    def _upload_video_to_s3(self, video_bytes: bytes, filename: str, prefix: str) -> Optional[str]:
        """Upload video bytes to S3 with a specific prefix."""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]

            if filename:
                name, ext = os.path.splitext(filename)
                s3_filename = f"{prefix}_{name}_{timestamp}_{unique_id}{ext}"
            else:
                s3_filename = f"{prefix}_video_{timestamp}_{unique_id}.mp4"

            # Upload to S3 using adapted uploader for videos
            return self._upload_video_bytes_to_s3(video_bytes, s3_filename)

        except Exception as e:
            print(f"⚠️  Error uploading video to S3: {e}")
            return None

    def _upload_video_bytes_to_s3(self, video_bytes: bytes, filename: str) -> Optional[str]:
        """
        Upload video bytes directly to S3.
        Adapted from the existing image uploader.
        """
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            from io import BytesIO

            # Load environment variables
            aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            bucket_name = os.getenv('S3_BUCKET_NAME')
            region = os.getenv('AWS_REGION', 'us-east-1')

            # Validate environment variables
            if not all([aws_access_key_id, aws_secret_access_key, bucket_name]):
                print("⚠️  Missing required AWS environment variables for S3 upload")
                return None

            # Initialize S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region
            )

            # Create S3 key for video
            s3_key = f"videos/{filename}"

            # Create BytesIO object from bytes
            bytes_io = BytesIO(video_bytes)

            # Upload the video
            extra_args = {
                'ContentType': 'video/mp4',
                'ContentDisposition': 'inline'
            }

            s3_client.upload_fileobj(
                bytes_io,
                bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )

            # Generate the S3 URL
            s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"

            print(f"📤 Video uploaded successfully to: {s3_url}")
            return s3_url

        except Exception as e:
            print(f"❌ Error uploading video to S3: {e}")
            return None


# Global service instance
fall_detection_service = FallDetectionService()


def is_fall_detection_available() -> bool:
    """Check if fall detection is available."""
    return ML_DEPENDENCIES_AVAILABLE and os.path.exists("./falldetect-11x.pt")


def initialize_fall_detection():
    """Initialize the fall detection model."""
    if ML_DEPENDENCIES_AVAILABLE:
        fall_detection_service.initialize_model()
    else:
        print("⚠️  Fall detection not available - YOLO dependencies not installed")


def process_video_for_fall_detection(video_bytes: bytes, filename: str = None, user_id: int = None, location: str = None) -> Dict[str, Any]:
    """
    Process video for fall detection.

    Args:
        video_bytes: Raw video bytes
        filename: Original filename
        user_id: Optional user ID
        location: Optional location

    Returns:
        Dictionary with detection results and S3 URLs
    """
    return fall_detection_service.process_video(video_bytes, filename, user_id, location)
