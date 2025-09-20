"""
Fall Detection API endpoints.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from schemas import FallDetectionResponse, SuccessResponse
from database.services import UserService

# Fall Detection imports
try:
    from services.fall_detection import (
        process_video_for_fall_detection,
        is_fall_detection_available,
        initialize_fall_detection
    )
    FALL_DETECTION_AVAILABLE = True
    print("✅ Fall detection service loaded")
except ImportError as e:
    print(f"⚠️  Fall detection service not available: {e}")
    FALL_DETECTION_AVAILABLE = False

router = APIRouter(prefix="/fall-detection", tags=["Fall Detection"])


@router.get("/status")
async def get_fall_detection_status():
    """
    Get fall detection service status and configuration.
    """
    if not FALL_DETECTION_AVAILABLE:
        return {
            "status": "unavailable",
            "service": "YOLO Fall Detection",
            "reason": "Service not available - missing dependencies or model file",
            "is_initialized": False,
            "model_available": False,
            "dependencies_available": False
        }

    try:
        model_available = is_fall_detection_available()

        return {
            "status": "available" if model_available else "model_missing",
            "service": "YOLO Fall Detection",
            "model_file": "falldetect-11x.pt",
            "is_initialized": True,
            "model_available": model_available,
            "dependencies_available": True,
            "supported_formats": ["mp4", "avi", "mov"],
            "max_file_size": "100MB"
        }

    except Exception as e:
        return {
            "status": "error",
            "service": "YOLO Fall Detection",
            "error": str(e),
            "is_initialized": False,
            "model_available": False,
            "dependencies_available": True
        }


@router.post("/analyze-video", response_model=FallDetectionResponse)
async def analyze_video_for_falls(
    video: UploadFile = File(...,
                             description="Video file to analyze for fall detection"),
    user_id: Optional[int] = Form(None, description="User ID (optional)"),
    location: Optional[str] = Form(
        None, description="Location where video was recorded (optional)")
):
    """
    Upload and analyze a video for fall detection.

    This endpoint:
    1. Receives a video file from the frontend
    2. Processes the video using YOLO fall detection model
    3. Uploads both original and processed videos to S3
    4. Returns fall detection results with S3 URLs

    The response follows the same pattern as EquipmentComplianceDisplay for consistency.
    """
    if not FALL_DETECTION_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Fall detection service not available. Please check YOLO dependencies and model file."
        )

    try:
        # Validate user exists if user_id is provided
        if user_id:
            user = UserService.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

        # Validate video file
        if not video.content_type or not video.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")

        # Check file size (optional - adjust limit as needed)
        max_size = 100 * 1024 * 1024  # 100MB
        video.file.seek(0, 2)  # Seek to end
        file_size = video.file.tell()
        video.file.seek(0)  # Reset to beginning

        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"Video file too large. Maximum size is {max_size // (1024*1024)}MB"
            )

        # Read video bytes
        video_bytes = await video.read()
        if len(video_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty video file")

        print(f"🎬 Processing video: {video.filename}")
        print(f"   File size: {len(video_bytes) / (1024*1024):.2f} MB")
        print(f"   Content type: {video.content_type}")
        print(f"   User ID: {user_id}")
        print(f"   Location: {location}")

        # Process video for fall detection
        try:
            result = process_video_for_fall_detection(
                video_bytes=video_bytes,
                filename=video.filename,
                user_id=user_id,
                location=location
            )

            # Create response in the format expected by frontend
            response = FallDetectionResponse(
                user_id=result.get('user_id'),
                location=result.get('location'),
                detection_result=result['detection_result'],
                original_video_url=result.get('original_video_url'),
                processed_video_url=result.get('processed_video_url'),
                processing_timestamp=result['processing_timestamp'],
                video_filename=result.get('video_filename')
            )

            print(f"✅ Fall detection analysis completed:")
            print(
                f"   Fall detected: {'YES' if result['detection_result']['fall_detected'] else 'NO'}")
            print(
                f"   Total detections: {result['detection_result']['total_detections']}")
            print(
                f"   Processing time: {result['detection_result']['processing_time']:.2f}s")
            print(f"   Original video URL: {result.get('original_video_url')}")
            print(
                f"   Processed video URL: {result.get('processed_video_url')}")

            return response

        except Exception as e:
            print(f"❌ Error during fall detection processing: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Fall detection processing failed: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in analyze_video_for_falls: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/initialize")
async def initialize_fall_detection_model():
    """
    Initialize the fall detection model.
    Useful for pre-loading the model for faster first requests.
    """
    if not FALL_DETECTION_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Fall detection service not available"
        )

    try:
        print("🤖 Initializing fall detection model...")
        initialize_fall_detection()

        return {
            "status": "success",
            "message": "Fall detection model initialized successfully",
            "model": "falldetect-11x",
            "ready": True
        }

    except Exception as e:
        print(f"❌ Error initializing fall detection model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Model initialization failed: {str(e)}"
        )


@router.get("/health")
async def fall_detection_health_check():
    """
    Health check endpoint for fall detection service.
    """
    if not FALL_DETECTION_AVAILABLE:
        return {
            "status": "unhealthy",
            "service": "Fall Detection",
            "available": False,
            "reason": "Service dependencies not available"
        }

    try:
        model_available = is_fall_detection_available()

        return {
            "status": "healthy" if model_available else "degraded",
            "service": "Fall Detection",
            "available": True,
            "model_ready": model_available,
            "timestamp": "2024-01-01T00:00:00Z"  # You can use datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Fall Detection",
            "available": False,
            "error": str(e)
        }
