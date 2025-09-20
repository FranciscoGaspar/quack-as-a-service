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

# Bedrock Analytics import for AI reports
try:
    from services.bedrock_analytics import bedrock_nlp
    BEDROCK_AVAILABLE = True
    print("✅ Bedrock analytics service loaded for AI reports")
except ImportError as e:
    print(f"⚠️  Bedrock analytics service not available: {e}")
    BEDROCK_AVAILABLE = False

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


@router.post("/generate-ai-report")
async def generate_ai_report_from_detection(
    video_data: dict
):
    """
    Generate an AI-powered report from existing fall detection results.

    This endpoint takes fall detection data and generates a comprehensive
    AI report with safety insights, risk assessment, and recommendations.
    """

    if not BEDROCK_AVAILABLE:
        # Return a basic fallback report
        return {
            "status": "success",
            "ai_report": {
                "report_type": "basic_fallback",
                "executive_summary": f"Fall detection analysis completed for video. {'Fall incident detected' if video_data.get('fall_detected', False) else 'No fall incidents detected'} during analysis.",
                "detailed_analysis": "Comprehensive AI analysis is temporarily unavailable. The fall detection system successfully processed the video and provided technical detection results.",
                "key_findings": [
                    f"Video processing completed in {video_data.get('processing_time', 0):.1f} seconds",
                    f"Fall detection status: {'Detected' if video_data.get('fall_detected', False) else 'Not detected'}",
                    f"Total detections: {video_data.get('total_detections', 0)}",
                    "Technical analysis completed successfully"
                ],
                "recommendations": [
                    "Review video footage for safety compliance assessment",
                    "Implement proper safety protocols if incidents were detected",
                    "Consider additional monitoring for high-risk areas",
                    "Ensure emergency response procedures are in place"
                ],
                "risk_level": "high" if video_data.get('fall_detected', False) else "low",
                "confidence_score": 85,
                "generated_at": video_data.get('analysis_timestamp', ''),
                "model_used": "fallback_analysis",
                "video_context": video_data
            }
        }

    try:
        # Create a comprehensive prompt for the AI analysis
        user_prompt = f"""
        Analyze this fall detection video analysis and provide a comprehensive safety report.
        
        Video Analysis Results:
        - Video Filename: {video_data.get('video_filename', 'Unknown')}
        - Location: {video_data.get('location', 'Unknown')}
        - Duration: {video_data.get('video_duration', 0):.2f} seconds
        - Fall Detected: {'Yes' if video_data.get('fall_detected', False) else 'No'}
        - Total Detections: {video_data.get('total_detections', 0)}
        - Confidence Scores: {video_data.get('confidence_scores', [])}
        - Processing Time: {video_data.get('processing_time', 0):.1f} seconds
        - Model Used: {video_data.get('model_version', 'Unknown')}
        
        Please provide a comprehensive safety analysis including:
        1. Executive summary of the incident/analysis
        2. Risk assessment and severity level
        3. Safety compliance evaluation
        4. Immediate action recommendations
        5. Long-term prevention strategies
        6. Regulatory compliance considerations
        
        Focus on workplace safety, incident prevention, and actionable insights.
        """

        # Use the direct AI model invocation instead of generate_custom_analysis
        if bedrock_nlp.is_initialized:
            ai_response = bedrock_nlp._invoke_model(
                user_prompt, max_tokens=1500, temperature=0.3)

            # Parse the response manually since we're not using the structured methods
            ai_report = {
                "report_type": "ai_video_analysis",
                "executive_summary": f"AI analysis completed for {video_data.get('video_filename', 'video')}. {'Fall incident detected requiring immediate attention' if video_data.get('fall_detected', False) else 'No fall incidents detected during monitoring period'}.",
                "detailed_analysis": ai_response,
                "key_findings": [
                    f"Video processing completed successfully in {video_data.get('processing_time', 0):.1f} seconds",
                    f"Fall detection status: {'DETECTED - Immediate attention required' if video_data.get('fall_detected', False) else 'NOT DETECTED - Normal activity observed'}",
                    f"Analysis confidence based on {video_data.get('total_detections', 0)} detection points",
                    f"Video duration: {video_data.get('video_duration', 0):.1f} seconds of footage analyzed"
                ],
                "recommendations": [
                    "Review complete video footage for comprehensive assessment" if video_data.get(
                        'fall_detected', False) else "Continue standard monitoring protocols",
                    "Implement immediate safety response procedures" if video_data.get(
                        'fall_detected', False) else "Maintain current safety standards",
                    "Document incident for safety compliance records" if video_data.get(
                        'fall_detected', False) else "File routine monitoring report",
                    "Consider additional safety measures for this location" if video_data.get(
                        'fall_detected', False) else "Evaluate current safety protocols effectiveness"
                ],
                "risk_level": "high" if video_data.get('fall_detected', False) else "low",
                "confidence_score": 90 if video_data.get('fall_detected', False) else 85,
                "generated_at": video_data.get('analysis_timestamp', ''),
                "model_used": bedrock_nlp.model_id,
                "video_context": video_data
            }
        else:
            # Fallback if AI is not available
            ai_report = {
                "report_type": "ai_video_analysis",
                "executive_summary": f"Technical analysis completed for {video_data.get('video_filename', 'video')}. {'Fall incident detected requiring immediate attention' if video_data.get('fall_detected', False) else 'No fall incidents detected during monitoring period'}.",
                "detailed_analysis": "Comprehensive AI analysis is temporarily unavailable. The fall detection system has successfully processed the video and provided technical detection results. Manual review of the footage is recommended for complete assessment.",
                "key_findings": [
                    f"Video processing completed successfully in {video_data.get('processing_time', 0):.1f} seconds",
                    f"Fall detection status: {'DETECTED - Immediate attention required' if video_data.get('fall_detected', False) else 'NOT DETECTED - Normal activity observed'}",
                    f"Analysis confidence based on {video_data.get('total_detections', 0)} detection points",
                    f"Video duration: {video_data.get('video_duration', 0):.1f} seconds of footage analyzed"
                ],
                "recommendations": [
                    "Review complete video footage for comprehensive assessment" if video_data.get(
                        'fall_detected', False) else "Continue standard monitoring protocols",
                    "Implement immediate safety response procedures" if video_data.get(
                        'fall_detected', False) else "Maintain current safety standards",
                    "Document incident for safety compliance records" if video_data.get(
                        'fall_detected', False) else "File routine monitoring report",
                    "Consider additional safety measures for this location" if video_data.get(
                        'fall_detected', False) else "Evaluate current safety protocols effectiveness"
                ],
                "risk_level": "high" if video_data.get('fall_detected', False) else "low",
                "confidence_score": 85,
                "generated_at": video_data.get('analysis_timestamp', ''),
                "model_used": "technical_analysis",
                "video_context": video_data
            }

        return {
            "status": "success",
            "ai_report": ai_report
        }

    except Exception as e:
        print(f"Error generating AI report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI report: {str(e)}"
        )
