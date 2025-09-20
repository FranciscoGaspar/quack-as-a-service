"""
Amazon Rekognition Emotional Recognition Service
Analyzes facial expressions in images to detect emotions using AWS Rekognition

This service provides emotional analysis capabilities for the compliance tracking system,
allowing for additional context about user emotional state during safety compliance checks.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from dotenv import load_dotenv
import os
import base64
from io import BytesIO
from PIL import Image

# Load environment variables
load_dotenv()

# AWS Rekognition Dependencies
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    REKOGNITION_AVAILABLE = True
    print("✅ AWS Rekognition library loaded")
except ImportError as e:
    print(f"⚠️  AWS Rekognition library not available: {e}")
    print("💡 Install with: pip install boto3")
    REKOGNITION_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmotionResult:
    """Emotional recognition result."""
    emotion: str
    confidence: float
    bounding_box: Optional[Dict[str, float]] = None

@dataclass
class FaceAnalysis:
    """Complete face analysis result."""
    face_id: str
    emotions: List[EmotionResult]
    age_range: Optional[Dict[str, int]] = None
    gender: Optional[Dict[str, Any]] = None
    bounding_box: Optional[Dict[str, float]] = None
    quality: Optional[Dict[str, float]] = None
    pose: Optional[Dict[str, float]] = None

@dataclass
class EmotionalAnalysisResponse:
    """Complete emotional analysis response."""
    faces_detected: int
    face_analyses: List[FaceAnalysis]
    dominant_emotion: str
    overall_confidence: float
    analysis_timestamp: datetime
    image_quality: str
    recommendations: List[str]

class RekognitionEmotionalAnalysis:
    """Amazon Rekognition-powered emotional analysis service."""
    
    def __init__(self, region_name: str = "us-east-1"):
        self.rekognition_client = None
        self.is_initialized = False
        self.region_name = region_name
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        # Emotion labels for better context
        self.emotion_labels = {
            'HAPPY': 'Happy',
            'SAD': 'Sad',
            'ANGRY': 'Angry',
            'CONFUSED': 'Confused',
            'DISGUSTED': 'Disgusted',
            'SURPRISED': 'Surprised',
            'CALM': 'Calm',
            'FEAR': 'Fear'
        }
        
        # Initialize Rekognition client
        self._initialize_rekognition()
    
    def _initialize_rekognition(self):
        """Initialize AWS Rekognition client."""
        if not REKOGNITION_AVAILABLE:
            logger.warning("AWS Rekognition library not available")
            return

        if not self.aws_access_key_id or not self.aws_secret_access_key:
            logger.error("❌ AWS credentials not found. Please configure AWS credentials.")
            return
        
        try:
            # Initialize Rekognition client
            self.rekognition_client = boto3.client(
                service_name='rekognition',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
            # Test the connection
            self._test_rekognition_connection()
            
            self.is_initialized = True
            logger.info(f"✅ AWS Rekognition client initialized successfully (Region: {self.region_name})")
            
        except NoCredentialsError:
            logger.error("❌ AWS credentials not found. Please configure AWS credentials.")
            self.is_initialized = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS Rekognition client: {e}")
            self.is_initialized = False
    
    def _test_rekognition_connection(self):
        """Test Rekognition connection by listing collections."""
        try:
            # Test with a simple request
            if not self.rekognition_client:
                raise Exception("Rekognition client not created")
            
            # Try to list collections (this is a lightweight operation)
            response = self.rekognition_client.list_collections(MaxResults=1)
            logger.info("✅ Rekognition connection test successful")
        except Exception as e:
            logger.error(f"❌ Rekognition connection test failed: {e}")
            raise
    
    def analyze_emotions_from_bytes(self, image_bytes: bytes) -> EmotionalAnalysisResponse:
        """Analyze emotions from image bytes."""
        if not self.is_initialized or not self.rekognition_client:
            return self._create_fallback_response("AWS Rekognition not available")
        
        try:
            # Validate image
            self._validate_image(image_bytes)
            
            # Analyze emotions using Rekognition
            response = self.rekognition_client.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['ALL']  # Get all available attributes including emotions
            )
            
            # Process the response
            analysis = self._process_rekognition_response(response)
            
            logger.info("✅ Emotional analysis completed successfully using AWS Rekognition")
            return analysis
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                raise Exception(f"Access denied to Rekognition. Please check IAM permissions.")
            elif error_code == 'InvalidImageFormatException':
                raise Exception(f"Invalid image format: {e}")
            elif error_code == 'ImageTooLargeException':
                raise Exception(f"Image too large: {e}")
            else:
                raise Exception(f"Rekognition API error: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to analyze emotions: {e}")
            return self._create_fallback_response(f"Error: {str(e)}")
    
    def analyze_emotions_from_pil_image(self, pil_image: Image.Image) -> EmotionalAnalysisResponse:
        """Analyze emotions from PIL Image object."""
        try:
            # Convert PIL image to bytes
            img_buffer = BytesIO()
            pil_image.save(img_buffer, format='JPEG', quality=95)
            image_bytes = img_buffer.getvalue()
            
            return self.analyze_emotions_from_bytes(image_bytes)
            
        except Exception as e:
            logger.error(f"❌ Failed to convert PIL image to bytes: {e}")
            return self._create_fallback_response(f"Image conversion error: {str(e)}")
    
    def _validate_image(self, image_bytes: bytes):
        """Validate image format and size."""
        if not image_bytes:
            raise ValueError("Empty image data")
        
        if len(image_bytes) > 15 * 1024 * 1024:  # 15MB limit for Rekognition
            raise ValueError("Image too large (max 15MB)")
        
        try:
            # Try to open with PIL to validate format
            img = Image.open(BytesIO(image_bytes))
            img.verify()
        except Exception as e:
            raise ValueError(f"Invalid image format: {str(e)}")
    
    def _process_rekognition_response(self, response: Dict[str, Any]) -> EmotionalAnalysisResponse:
        """Process Rekognition API response into structured format."""
        faces = response.get('FaceDetails', [])
        faces_detected = len(faces)
        
        face_analyses = []
        all_emotions = []
        
        for i, face in enumerate(faces):
            # Extract emotions
            emotions = []
            for emotion_data in face.get('Emotions', []):
                emotion_result = EmotionResult(
                    emotion=emotion_data['Type'],
                    confidence=emotion_data['Confidence'],
                    bounding_box=face.get('BoundingBox')
                )
                emotions.append(emotion_result)
                all_emotions.append(emotion_result)
            
            # Extract other face attributes
            age_range = face.get('AgeRange')
            gender = face.get('Gender')
            bounding_box = face.get('BoundingBox')
            quality = face.get('Quality')
            pose = face.get('Pose')
            
            face_analysis = FaceAnalysis(
                face_id=f"face_{i+1}",
                emotions=emotions,
                age_range=age_range,
                gender=gender,
                bounding_box=bounding_box,
                quality=quality,
                pose=pose
            )
            face_analyses.append(face_analysis)
        
        # Determine dominant emotion across all faces
        if all_emotions:
            dominant_emotion = max(all_emotions, key=lambda x: x.confidence)
            overall_confidence = dominant_emotion.confidence
            dominant_emotion_name = dominant_emotion.emotion
        else:
            dominant_emotion_name = "UNKNOWN"
            overall_confidence = 0.0
        
        # Generate recommendations based on analysis
        recommendations = self._generate_recommendations(face_analyses, dominant_emotion_name, overall_confidence)
        
        # Assess image quality
        image_quality = self._assess_image_quality(face_analyses)
        
        return EmotionalAnalysisResponse(
            faces_detected=faces_detected,
            face_analyses=face_analyses,
            dominant_emotion=dominant_emotion_name,
            overall_confidence=overall_confidence,
            analysis_timestamp=datetime.now(),
            image_quality=image_quality,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, face_analyses: List[FaceAnalysis], dominant_emotion: str, confidence: float) -> List[str]:
        """Generate recommendations based on emotional analysis."""
        recommendations = []
        
        if confidence < 50:
            recommendations.append("Low confidence in emotion detection - consider retaking photo with better lighting")
        
        if dominant_emotion in ['SAD', 'ANGRY', 'CONFUSED']:
            recommendations.append("Consider checking on employee wellbeing")
            recommendations.append("Review safety training materials for clarity")
        
        if dominant_emotion == 'FEAR':
            recommendations.append("Address any safety concerns immediately")
            recommendations.append("Ensure proper safety equipment training")
        
        if dominant_emotion == 'HAPPY':
            recommendations.append("Positive emotional state detected - good for safety compliance")
        
        if len(face_analyses) > 1:
            recommendations.append("Multiple faces detected - ensure individual compliance checks")
        
        if not recommendations:
            recommendations.append("Emotional analysis completed - no specific recommendations")
        
        return recommendations
    
    def _assess_image_quality(self, face_analyses: List[FaceAnalysis]) -> str:
        """Assess overall image quality based on face analyses."""
        if not face_analyses:
            return "no_faces"
        
        quality_scores = []
        for face in face_analyses:
            if face.quality:
                brightness = face.quality.get('Brightness', 50)
                sharpness = face.quality.get('Sharpness', 50)
                # Simple quality assessment
                quality_score = (brightness + sharpness) / 2
                quality_scores.append(quality_score)
        
        if not quality_scores:
            return "unknown"
        
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        if avg_quality >= 70:
            return "excellent"
        elif avg_quality >= 50:
            return "good"
        elif avg_quality >= 30:
            return "fair"
        else:
            return "poor"
    
    def _create_fallback_response(self, reason: str) -> EmotionalAnalysisResponse:
        """Create fallback response when Rekognition is not available."""
        return EmotionalAnalysisResponse(
            faces_detected=0,
            face_analyses=[],
            dominant_emotion="UNKNOWN",
            overall_confidence=0.0,
            analysis_timestamp=datetime.now(),
            image_quality="unknown",
            recommendations=[f"Emotional analysis unavailable: {reason}"]
        )
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status and configuration."""
        return {
            "service": "AWS Rekognition",
            "is_initialized": self.is_initialized,
            "region": self.region_name,
            "available_emotions": list(self.emotion_labels.keys()),
            "capabilities": [
                "emotion_detection",
                "face_analysis",
                "age_detection",
                "gender_detection",
                "pose_estimation"
            ] if self.is_initialized else []
        }

# Global instance
rekognition_emotions = RekognitionEmotionalAnalysis()
