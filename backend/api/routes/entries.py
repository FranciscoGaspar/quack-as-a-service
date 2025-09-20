"""
Personal entry management endpoints.
"""

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse
import hashlib
import json

from database.services import UserService, PersonalEntryService
from utils.s3_uploader import upload_image_bytes_to_s3
from core.room_equipment_config import RoomEquipmentConfig
from PIL import Image
import io

# AI Analytics imports
try:
    from services.bedrock_analytics import bedrock_nlp
    AI_ANALYTICS_AVAILABLE = True
    print("✅ AWS Bedrock Analytics service loaded")
except ImportError as e:
    print(f"⚠️  AWS Bedrock Analytics not available: {e}")
    AI_ANALYTICS_AVAILABLE = False

# Emotional Recognition imports
try:
    from services.rekognition_emotions import rekognition_emotions
    EMOTIONAL_RECOGNITION_AVAILABLE = True
    print("✅ AWS Rekognition Emotional Analysis service loaded")
except ImportError as e:
    print(f"⚠️  AWS Rekognition Emotional Analysis not available: {e}")
    EMOTIONAL_RECOGNITION_AVAILABLE = False

# Optional ML dependencies - import only if available
try:
    import image_detection
    ML_DEPENDENCIES_AVAILABLE = True
    print("✅ ML dependencies loaded - image detection enabled")
    
    # Pre-initialize model on startup for faster first request
    try:
        print("🚀 Pre-loading ML model for faster first request...")
        image_detection.initialize_model()
        print("✅ ML model pre-loaded successfully")
    except Exception as e:
        print(f"⚠️  Could not pre-load ML model: {e}")
        print("💡 Model will be loaded on first request (slower)")
        
except ImportError as e:
    print(f"⚠️  ML dependencies not available - image detection disabled: {e}")
    print("💡 To enable image detection, install: pip install torch torchvision transformers")
    ML_DEPENDENCIES_AVAILABLE = False
from schemas import (
    PersonalEntryCreate, PersonalEntryUpdate, PersonalEntryResponse,
    PersonalEntryBaseResponse, EquipmentUpdate, SuccessResponse
)

router = APIRouter(prefix="/entries", tags=["Personal Entries"])

# Simple in-memory cache for AI analysis
ai_analysis_cache = {}
CACHE_DURATION_SECONDS = 300  # 5 minutes cache


def _generate_cache_key(limit: int) -> str:
    """Generate a cache key for AI analysis based on parameters."""
    cache_data = {
        "limit": limit,
        "endpoint": "emotional_ai_analysis"
    }
    cache_string = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(cache_string.encode()).hexdigest()


def _is_cache_valid(cache_entry: dict) -> bool:
    """Check if cache entry is still valid."""
    if not cache_entry:
        return False
    
    cache_time = cache_entry.get("timestamp", 0)
    current_time = datetime.now(timezone.utc).timestamp()
    
    return (current_time - cache_time) < CACHE_DURATION_SECONDS


def _get_cached_analysis(cache_key: str) -> Optional[dict]:
    """Get cached AI analysis if valid."""
    cache_entry = ai_analysis_cache.get(cache_key)
    
    if cache_entry and _is_cache_valid(cache_entry):
        print(f"🎯 Cache HIT for AI analysis (key: {cache_key[:8]}...)")
        cached_data = cache_entry.get("data").copy()
        cached_data["cache_info"] = {
            "cached": True,
            "cache_key": cache_key[:8] + "...",
            "cache_duration_seconds": CACHE_DURATION_SECONDS
        }
        return cached_data
    
    if cache_entry:
        print(f"⏰ Cache EXPIRED for AI analysis (key: {cache_key[:8]}...)")
        # Remove expired entry
        del ai_analysis_cache[cache_key]
    
    return None


def _set_cached_analysis(cache_key: str, analysis_data: dict) -> None:
    """Cache AI analysis data."""
    ai_analysis_cache[cache_key] = {
        "data": analysis_data,
        "timestamp": datetime.now(timezone.utc).timestamp()
    }
    print(f"💾 Cached AI analysis (key: {cache_key[:8]}..., expires in {CACHE_DURATION_SECONDS}s)")


def _add_computed_fields(entry) -> PersonalEntryResponse:
    """Add computed fields to entry response."""
    # Ensure approval status is calculated if missing
    if entry.is_approved is None:
        try:
            entry.calculate_and_set_approval_status()
        except Exception as e:
            print(f"⚠️  Could not calculate approval status for entry {entry.id}: {e}")
    
    # First validate with base schema (includes new approval fields)
    base_data = PersonalEntryBaseResponse.model_validate(entry)
    
    # Fetch user name if user_id is present
    user_name = None
    if entry.user_id:
        try:
            user = UserService.get_by_id(entry.user_id)
            if user:
                user_name = user.name
        except Exception as e:
            print(f"⚠️  Could not fetch user name for user_id {entry.user_id}: {e}")
            user_name = None
    
    # Then create full response with computed fields
    return PersonalEntryResponse(
        **base_data.model_dump(),
        is_compliant=entry.is_compliant(),
        missing_equipment=entry.get_missing_equipment(),
        user_name=user_name
    )


@router.post("", response_model=PersonalEntryResponse)
async def create_entry(entry: PersonalEntryCreate):
    """Create a new personal entry."""
    try:
        db_entry = PersonalEntryService.create(
            user_id=entry.user_id,
            room_name=entry.room_name,
            equipment=entry.equipment,
            image_url=entry.image_url
        )
        return _add_computed_fields(db_entry)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/emotional-analysis-summary")
async def get_all_emotional_analysis(
    limit: Optional[int] = Query(100, ge=1, le=1000, description="Limit number of results"),
    emotion_filter: Optional[str] = Query(None, description="Filter by dominant emotion (e.g., 'HAPPY', 'SAD', 'ANGRY')"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=100.0, description="Minimum confidence threshold")
):
    """
    Get emotional analysis data for all entries.
    
    Returns comprehensive emotional analysis data including:
    - All entries with emotional analysis
    - Filtering by emotion type and confidence
    - Summary statistics
    - Emotional trends across entries
    """
    try:
        # Get all entries with emotional analysis
        entries = PersonalEntryService.get_all(limit=limit)
        
        # Filter entries that have emotional analysis
        entries_with_analysis = [entry for entry in entries if entry.emotional_analysis]
        
        if not entries_with_analysis:
            return {
                "status": "no_data",
                "message": "No entries with emotional analysis found",
                "total_entries": len(entries),
                "entries_with_analysis": 0,
                "emotional_analysis": []
            }
        
        # Convert to analysis data
        analysis_data = []
        emotion_counts = {}
        confidence_scores = []
        
        for entry in entries_with_analysis:
            analysis = entry.emotional_analysis
            
            # Apply filters
            if emotion_filter and analysis.dominant_emotion != emotion_filter:
                continue
            
            if min_confidence and analysis.overall_confidence < min_confidence:
                continue
            
            analysis_dict = analysis.to_dict()
            analysis_dict['entry'] = {
                'id': entry.id,
                'user_id': entry.user_id,
                'room_name': entry.room_name,
                'entered_at': entry.entered_at.isoformat()
            }
            
            analysis_data.append(analysis_dict)
            
            # Collect statistics
            emotion = analysis.dominant_emotion
            if emotion:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            if analysis.overall_confidence:
                confidence_scores.append(analysis.overall_confidence)
        
        # Calculate summary statistics
        total_analyzed = len(analysis_data)
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Find most common emotion
        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1]) if emotion_counts else None
        
        return {
            "status": "success",
            "summary": {
                "total_entries": len(entries),
                "entries_with_analysis": len(entries_with_analysis),
                "filtered_results": total_analyzed,
                "average_confidence": round(avg_confidence, 2),
                "emotion_distribution": emotion_counts,
                "most_common_emotion": most_common_emotion[0] if most_common_emotion else None,
                "most_common_emotion_count": most_common_emotion[1] if most_common_emotion else 0
            },
            "filters_applied": {
                "emotion_filter": emotion_filter,
                "min_confidence": min_confidence
            },
            "emotional_analysis": analysis_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve emotional analysis data: {str(e)}")


@router.get("/ai/emotional-analysis")
async def get_emotional_ai_analysis(
    limit: Optional[int] = Query(100, ge=10, le=500, description="Number of entries to analyze")
):
    """
    Generate AI-powered emotional analysis using AWS Bedrock.
    
    Provides comprehensive emotional analysis including:
    - Executive summary of emotional climate
    - Key findings about employee emotional well-being
    - Risk assessment for workplace mental health
    - Actionable recommendations for improving emotional culture
    - Workplace psychology insights
    
    This endpoint is cached for 5 minutes to improve performance.
    """
    if not AI_ANALYTICS_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="AI Analytics service not available. Please check AWS Bedrock configuration."
        )
    
    try:
        # Generate cache key based on parameters
        cache_key = _generate_cache_key(limit)
        
        # Check cache first
        cached_result = _get_cached_analysis(cache_key)
        if cached_result:
            return cached_result
        
        # Cache miss - generate new analysis
        print(f"🔄 Cache MISS for AI analysis (key: {cache_key[:8]}...) - generating new analysis")
        
        # Get entries for analysis
        entries = PersonalEntryService.get_all(limit=limit)
        
        if len(entries) < 5:
            raise HTTPException(
                status_code=400,
                detail="Need at least 5 entries for emotional analysis"
            )
        
        # Generate emotional analysis
        insight = await bedrock_nlp.generate_emotional_analysis(entries)
        
        # Prepare response
        response_data = {
            "status": "success",
            "emotional_analysis": {
                "type": insight.insight_type,
                "title": insight.title,
                "summary": insight.summary,
                "detailed_analysis": insight.detailed_analysis,
                "key_findings": insight.key_findings,
                "recommendations": insight.recommendations,
                "risk_level": insight.risk_level,
                "confidence_score": insight.confidence_score,
                "generated_at": insight.generated_at.isoformat(),
                "data_period": insight.data_period
            },
            "data_summary": {
                "entries_analyzed": len(entries),
                "analysis_type": "emotional_analysis",
                "ai_service": "AWS Bedrock"
            },
            "cache_info": {
                "cached": False,
                "cache_key": cache_key[:8] + "...",
                "cache_duration_seconds": CACHE_DURATION_SECONDS
            }
        }
        
        # Cache the result
        _set_cached_analysis(cache_key, response_data)
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emotional analysis failed: {str(e)}")


@router.get("/ai/cache-status")
async def get_cache_status():
    """
    Get AI analysis cache status and statistics.
    
    Returns information about:
    - Number of cached entries
    - Cache duration settings
    - Cache hit/miss statistics
    """
    try:
        current_time = datetime.now(timezone.utc).timestamp()
        
        # Count valid cache entries
        valid_entries = 0
        expired_entries = 0
        
        for cache_key, cache_entry in ai_analysis_cache.items():
            if _is_cache_valid(cache_entry):
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            "status": "success",
            "cache_info": {
                "total_entries": len(ai_analysis_cache),
                "valid_entries": valid_entries,
                "expired_entries": expired_entries,
                "cache_duration_seconds": CACHE_DURATION_SECONDS,
                "cache_duration_minutes": CACHE_DURATION_SECONDS / 60
            },
            "cache_keys": [
                {
                    "key": key[:8] + "...",
                    "valid": _is_cache_valid(entry),
                    "age_seconds": current_time - entry.get("timestamp", 0)
                }
                for key, entry in ai_analysis_cache.items()
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache status: {str(e)}")


@router.delete("/ai/cache")
async def clear_cache():
    """
    Clear all AI analysis cache entries.
    
    This will force the next AI analysis request to generate fresh data.
    """
    try:
        cache_count = len(ai_analysis_cache)
        ai_analysis_cache.clear()
        
        return {
            "status": "success",
            "message": f"Cleared {cache_count} cache entries",
            "cache_cleared": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@router.get("", response_model=List[PersonalEntryResponse])
async def get_entries(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results")
):
    """Get all personal entries."""
    try:
        entries = PersonalEntryService.get_all_with_users(limit=limit)
        return [_add_computed_fields(entry) for entry in entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entry_id}", response_model=PersonalEntryResponse)
async def get_entry(entry_id: int):
    """Get a personal entry by ID."""
    try:
        entry = PersonalEntryService.get_by_id(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        return _add_computed_fields(entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{entry_id}", response_model=PersonalEntryResponse)
async def update_entry(entry_id: int, entry: PersonalEntryUpdate):
    """Update a personal entry."""
    try:
        db_entry = PersonalEntryService.get_by_id(entry_id)
        if not db_entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        updated_entry = PersonalEntryService.update(
            entry_id,
            room_name=entry.room_name,
            equipment=entry.equipment,
            image_url=entry.image_url
        )
        return _add_computed_fields(updated_entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{entry_id}/equipment", response_model=PersonalEntryResponse)
async def update_entry_equipment(entry_id: int, equipment: EquipmentUpdate):
    """Update specific equipment items for an entry."""
    try:
        db_entry = PersonalEntryService.get_by_id(entry_id)
        if not db_entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        # Convert to dict, excluding None values
        equipment_dict = equipment.dict(exclude_none=True)
        if not equipment_dict:
            raise HTTPException(status_code=400, detail="No equipment updates provided")
        
        updated_entry = PersonalEntryService.update_equipment(entry_id, **equipment_dict)
        return _add_computed_fields(updated_entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{entry_id}", response_model=SuccessResponse)
async def delete_entry(entry_id: int):
    """Delete a personal entry."""
    try:
        entry = PersonalEntryService.get_by_id(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        PersonalEntryService.delete(entry_id)
        return SuccessResponse(message=f"Entry {entry_id} deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entry_id}/emotional-analysis")
async def get_emotional_analysis(entry_id: int):
    """
    Get emotional analysis results for a specific entry.
    
    Returns detailed emotional analysis data including:
    - Faces detected
    - Dominant emotion and confidence
    - Image quality assessment
    - Complete analysis data from AWS Rekognition
    - Recommendations based on emotional state
    """
    try:
        # Get the entry first to ensure it exists
        entry = PersonalEntryService.get_by_id(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        # Check if emotional analysis exists for this entry
        if not entry.emotional_analysis:
            return {
                "status": "no_analysis",
                "message": "No emotional analysis available for this entry",
                "entry_id": entry_id,
                "emotional_analysis": None
            }
        
        # Return the emotional analysis data
        return {
            "status": "success",
            "entry_id": entry_id,
            "emotional_analysis": entry.emotional_analysis.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve emotional analysis: {str(e)}")


@router.post("/upload-image", response_model=PersonalEntryResponse)
async def upload_image_and_analyze(
    image: UploadFile = File(..., description="Image file to analyze"),
    room_name: str = Form(..., description="Room name"),
    user_id: int = Form(..., description="User ID (required)"),
    create_annotated: bool = Form(True, description="Whether to create annotated image (slower but more detailed)")
):
    """
    Upload an image, analyze it for security equipment, store in S3, and create database entry.
    
    This endpoint:
    1. Receives an image file from the frontend
    2. Analyzes the image for security equipment using AI object detection (mask, gloves, hairnet)
    3. Uploads the annotated image to S3
    4. Creates a personal entry in the database with detected equipment and provided user
    5. Returns the standard personal entry response with compliance status
    
    Notes:
    - user_id is required - use /detect-user endpoint first to identify user from QR code
    - This endpoint focuses on equipment detection and entry creation
    - For user identification via QR codes, use the separate /detect-user endpoint
    """
    try:
        # Validate user exists
        user = UserService.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image bytes
        image_bytes = await image.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Convert image bytes to PIL Image for analysis
        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            # Ensure image is in RGB format to avoid channel dimension issues
            if pil_image.mode != 'RGB':
                print(f"🔄 Converting uploaded image from {pil_image.mode} to RGB for processing")
                pil_image = pil_image.convert('RGB')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")
        
        # Get room-specific detection parameters
        text_queries = RoomEquipmentConfig.get_detection_queries(room_name)
        required_equipment = RoomEquipmentConfig.get_required_equipment(room_name)
        detection_threshold = 0.4
        
        print(f"🏠 Room: {room_name}")
        print(f"📋 Required equipment: {required_equipment}")
        print(f"🔍 Detection queries: {text_queries}")
        print(f"📊 Room description: {RoomEquipmentConfig.get_room_description(room_name)}")
        
        # Initialize the detection model and perform analysis
        if ML_DEPENDENCIES_AVAILABLE:
            try:
                # Check if model is already loaded (faster)
                if not image_detection.is_model_ready():
                    print("🤖 Loading AI detection model...")
                    image_detection.initialize_model()
                else:
                    print("🤖 Using pre-loaded AI detection model")
                
                print(f"🔍 Analyzing image for safety equipment...")
                print(f"   Detection queries: {text_queries}")
                print(f"   Threshold: {detection_threshold}")
                
                # Use optimized combined detection for equipment and body parts only
                equipment_results, body_parts_results = image_detection.detect_equipment_and_body_parts(
                    image=pil_image,
                    equipment_queries=text_queries,
                    threshold=detection_threshold
                )
                
                # Analyze detection results for compliance using room-specific requirements
                analysis = image_detection.analyze_detection_results(equipment_results, required_equipment)
                
                # Store results for later use
                detection_results = equipment_results
                
            except Exception as e:
                print(f"❌ Error during image detection: {e}")
                # Continue with empty detection results if AI fails
                analysis = {
                    'total_detected': 0,
                    'compliance_status': False,
                    'found_items': {},
                    'missing_items': required_equipment
                }
                detection_results = [{'boxes': [], 'scores': [], 'labels': []}]
                body_parts_results = [{'boxes': [], 'scores': [], 'labels': []}]
        else:
            print("⚠️  Equipment detection skipped - ML dependencies not available")
            print("📸 Image uploaded successfully, but equipment detection is disabled")
            # Provide default values when ML is not available
            analysis = {
                'total_detected': 0,
                'compliance_status': False,  # Assume non-compliant when can't detect
                'found_items': {},
                'missing_items': required_equipment
            }
            detection_results = [{'boxes': [], 'scores': [], 'labels': []}]
            body_parts_results = [{'boxes': [], 'scores': [], 'labels': []}]
        
        # Create analysis result in expected format
        analysis_result = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "detection_threshold": detection_threshold,
            "total_detected": analysis['total_detected'],
            "compliance_status": analysis['compliance_status'],
            "found_items": analysis['found_items'],
            "missing_items": analysis['missing_items'],
            "raw_detection_results": detection_results
        }
        
        # Create annotated image with detection boxes for S3 upload
        try:
            if ML_DEPENDENCIES_AVAILABLE and create_annotated:
                print("📸 Creating annotated image with detection boxes...")
                # Parse text_queries to get individual items for visualization
                required_items = ['mask', 'glove', 'hairnet']
                
                # Use optimized annotation creation with pre-computed body parts
                annotated_image_bytes = image_detection.create_annotated_image(
                    image=pil_image,
                    results=detection_results,
                    text_queries=required_items,
                    missing_items=analysis['missing_items'],
                    body_parts_results=body_parts_results  # Reuse pre-computed results
                )
                
                # Generate filename for annotated image
                annotated_filename = f"annotated_{image.filename}" if image.filename else "annotated_image.png"
                
                # Upload annotated image to S3
                image_url = upload_image_bytes_to_s3(annotated_image_bytes, annotated_filename)
                print(f"✅ Annotated image created and uploaded successfully")
            elif ML_DEPENDENCIES_AVAILABLE and not create_annotated:
                # Use fast simple annotation
                print("📸 Creating simple annotated image...")
                annotated_image_bytes = image_detection.create_simple_annotated_image(
                    image=pil_image,
                    results=detection_results,
                    missing_items=analysis['missing_items']
                )
                
                # Generate filename for annotated image
                annotated_filename = f"simple_{image.filename}" if image.filename else "simple_image.png"
                
                # Upload annotated image to S3
                image_url = upload_image_bytes_to_s3(annotated_image_bytes, annotated_filename)
                print(f"✅ Simple annotated image created and uploaded successfully")
            else:
                # Fallback: upload original image if ML not available
                print("📸 Uploading original image (ML not available for annotation)")
                image_url = upload_image_bytes_to_s3(image_bytes, image.filename)
                
            if not image_url:
                # For development, we can continue without S3 upload
                print("Warning: S3 upload failed or not configured. Continuing without image URL.")
                image_url = None
                
        except Exception as e:
            print(f"Error creating/uploading annotated image: {e}")
            print("Falling back to original image upload...")
            # Fallback to original image if annotation fails
            image_url = upload_image_bytes_to_s3(image_bytes, image.filename)
            if not image_url:
                print("Warning: S3 upload failed or not configured. Continuing without image URL.")
                image_url = None
        
        # Convert detection results to equipment format expected by database
        equipment_detected = {}
        
        # Map detected items to equipment fields
        for item, details in analysis['found_items'].items():
            if 'mask' in item.lower():
                equipment_detected['mask'] = True
            elif 'glove' in item.lower():
                equipment_detected['gloves'] = True
            elif 'hairnet' in item.lower():
                equipment_detected['hairnet'] = True
        
        # Set missing items to False
        for missing_item in analysis['missing_items']:
            if 'mask' in missing_item.lower():
                equipment_detected['mask'] = False
            elif 'glove' in missing_item.lower():
                equipment_detected['gloves'] = False
            elif 'hairnet' in missing_item.lower():
                equipment_detected['hairnet'] = False
        
        # Use the provided user_id (already validated above)
        final_user_id = user_id
        
        print(f"🔍 Image analysis completed:")
        print(f"   Total detected: {analysis['total_detected']}")
        print(f"   Compliance: {'✅ COMPLIANT' if analysis['compliance_status'] else '❌ NON-COMPLIANT'}")
        print(f"   Equipment detected: {equipment_detected}")
        if analysis['found_items']:
            for item, details in analysis['found_items'].items():
                print(f"   ✅ {item}: {details['confidence']:.3f} confidence")
        if analysis['missing_items']:
            for item in analysis['missing_items']:
                print(f"   ❌ {item}: NOT DETECTED")
        
        # Perform emotional analysis if service is available
        emotional_analysis_result = None
        if EMOTIONAL_RECOGNITION_AVAILABLE:
            try:
                print(f"😊 Starting emotional analysis...")
                emotional_analysis_result = rekognition_emotions.analyze_emotions_from_pil_image(pil_image)
                print(f"😊 Emotional analysis completed:")
                print(f"   Faces detected: {emotional_analysis_result.faces_detected}")
                print(f"   Dominant emotion: {emotional_analysis_result.dominant_emotion}")
                print(f"   Confidence: {emotional_analysis_result.overall_confidence:.1f}%")
                print(f"   Image quality: {emotional_analysis_result.image_quality}")
            except Exception as e:
                print(f"⚠️  Emotional analysis failed: {e}")
                emotional_analysis_result = None
        else:
            print("⚠️  Emotional analysis skipped - AWS Rekognition not available")
        
        # Create database entry
        db_entry = PersonalEntryService.create(
            user_id=final_user_id,
            room_name=room_name,
            equipment=equipment_detected,
            image_url=image_url
        )
        
        # Add emotional analysis results to the database entry if available
        if emotional_analysis_result:
            try:
                # Import EmotionalAnalysis model
                from database.models import EmotionalAnalysis
                
                # Create emotional analysis record
                emotional_analysis = EmotionalAnalysis(
                    personal_entry_id=db_entry.id
                )
                emotional_analysis.set_analysis_results(emotional_analysis_result)
                
                # Save the emotional analysis to database
                from database.connection import create_session
                session = create_session()
                try:
                    session.add(emotional_analysis)
                    session.commit()
                    print("✅ Emotional analysis results saved to separate table")
                finally:
                    session.close()
            except Exception as e:
                print(f"⚠️  Failed to save emotional analysis to database: {e}")
        
        # Refetch the entry with emotional analysis relationship loaded
        # This is necessary because the original db_entry was created in a closed session
        try:
            entry_with_analysis = PersonalEntryService.get_by_id(db_entry.id)
            if entry_with_analysis:
                return _add_computed_fields(entry_with_analysis)
            else:
                # Fallback to original entry if refetch fails
                return _add_computed_fields(db_entry)
        except Exception as e:
            print(f"⚠️  Could not refetch entry with emotional analysis: {e}")
            # Fallback to original entry
            return _add_computed_fields(db_entry)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in upload_image_and_analyze: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Additional endpoints with different URL patterns
from fastapi import APIRouter as BaseRouter

# Create separate routers for user and room-based queries
user_entries_router = BaseRouter(prefix="/users", tags=["Personal Entries"])
room_entries_router = BaseRouter(prefix="/rooms", tags=["Personal Entries"])


@user_entries_router.get("/{user_id}/entries", response_model=List[PersonalEntryResponse])
async def get_user_entries(
    user_id: int,
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results")
):
    """Get all entries for a specific user."""
    try:
        # Check if user exists
        user = UserService.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        entries = PersonalEntryService.get_by_user(user_id, limit=limit)
        return [_add_computed_fields(entry) for entry in entries]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@room_entries_router.get("/{room_name}/entries", response_model=List[PersonalEntryResponse])
async def get_room_entries(
    room_name: str,
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results")
):
    """Get all entries for a specific room."""
    try:
        entries = PersonalEntryService.get_by_room(room_name, limit=limit)
        return [_add_computed_fields(entry) for entry in entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AI-POWERED ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/ai/status")
async def get_ai_status():
    """
    Get AI service status and configuration.
    """
    if not AI_ANALYTICS_AVAILABLE:
        return {
            "status": "unavailable",
            "service": "AWS Bedrock Analytics",
            "reason": "Service not available",
            "is_initialized": False,
            "capabilities": []
        }
    
    try:
        # Get service status
        is_initialized = bedrock_nlp.is_initialized
        
        return {
            "status": "success",
            "service": "AWS Bedrock Analytics",
            "model": bedrock_nlp.model_id,
            "region": bedrock_nlp.region_name,
            "is_initialized": is_initialized,
            "capabilities": [
                "compliance_insights",
                "executive_reports", 
                "anomaly_analysis",
                "quick_insights"
            ] if is_initialized else []
        }
        
    except Exception as e:
        return {
            "status": "error",
            "service": "AWS Bedrock Analytics",
            "error": str(e),
            "is_initialized": False,
            "capabilities": []
        }


@router.post("/ai/custom-analysis")
async def generate_custom_analysis(
    user_prompt: str = Form(..., description="User's question or prompt for AI analysis"),
    limit: Optional[int] = Query(100, ge=10, le=500, description="Number of entries to analyze")
):
    """
    Generate AI analysis based on user's custom prompt/question.
    
    Allows users to ask specific questions about their compliance data and get
    AI-powered insights tailored to their question.
    """
    if not AI_ANALYTICS_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="AI Analytics service not available. Please check AWS Bedrock configuration."
        )
    
    try:
        if not user_prompt.strip():
            raise HTTPException(
                status_code=400,
                detail="User prompt cannot be empty"
            )
        
        # Get entries for analysis
        entries = PersonalEntryService.get_all_with_users(limit=limit)
        
        if len(entries) < 5:
            raise HTTPException(
                status_code=400,
                detail="Need at least 5 entries for AI analysis"
            )
        
        # Generate custom AI analysis
        insight = await bedrock_nlp.generate_custom_analysis(entries, user_prompt)
        
        return {
            "status": "success",
            "analysis": {
                "type": insight.insight_type,
                "title": insight.title,
                "summary": insight.summary,
                "detailed_analysis": insight.detailed_analysis,
                "key_findings": insight.key_findings,
                "recommendations": insight.recommendations,
                "risk_level": insight.risk_level,
                "confidence_score": insight.confidence_score,
                "generated_at": insight.generated_at.isoformat(),
                "data_period": insight.data_period
            },
            "user_prompt": user_prompt,
            "data_summary": {
                "entries_analyzed": len(entries),
                "analysis_type": "custom",
                "ai_service": "AWS Bedrock"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom analysis failed: {str(e)}")


@router.post("/ai/quick-answer")
async def get_quick_answer(
    question: str = Form(..., description="User's question for quick AI answer"),
    limit: Optional[int] = Query(50, ge=5, le=200, description="Number of entries to analyze")
):
    """
    Get a quick AI answer to a user's question about compliance data.
    
    Provides concise, direct answers to specific questions about compliance patterns,
    equipment violations, room performance, etc.
    """
    if not AI_ANALYTICS_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "AI service not available",
            "answer": "AI service not available. Please check AWS Bedrock configuration."
        }
    
    try:
        if not question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )
        
        # Get entries for analysis
        entries = PersonalEntryService.get_all_with_users(limit=limit)
        
        if len(entries) < 5:
            return {
                "status": "insufficient_data",
                "message": "Need at least 5 entries for analysis",
                "answer": "Insufficient data for analysis. Please collect more compliance data."
            }
        
        # Generate quick answer
        answer = await bedrock_nlp.generate_quick_answer(entries, question)
        
        return {
            "status": "success",
            "question": question,
            "answer": answer,
            "data_summary": {
                "entries_analyzed": len(entries),
                "analysis_type": "quick_answer"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "message": f"Quick answer generation failed: {str(e)}",
            "answer": f"Sorry, I couldn't process your question. Error: {str(e)}"
        }


@router.get("/ai/insights")
async def get_ai_insights(
    insight_type: str = Query("comprehensive", regex="^(comprehensive|executive|anomaly|trend)$"),
    limit: Optional[int] = Query(100, ge=10, le=500, description="Number of entries to analyze")
):
    """
    Get AI-powered compliance insights using AWS Bedrock.
    
    Generates intelligent analysis of compliance data including:
    - Executive summary
    - Key findings and patterns
    - Risk assessment
    - Actionable recommendations
    """
    if not AI_ANALYTICS_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="AI Analytics service not available. Please check AWS Bedrock configuration."
        )
    
    try:
        # Get entries for analysis
        entries = PersonalEntryService.get_all_with_users(limit=limit)
        
        if len(entries) < 5:
            raise HTTPException(
                status_code=400,
                detail="Need at least 5 entries for AI analysis"
            )
        
        # Generate AI insights
        insight = await bedrock_nlp.generate_compliance_insights(entries, insight_type)
        
        return {
            "status": "success",
            "insight": {
                "type": insight.insight_type,
                "title": insight.title,
                "summary": insight.summary,
                "detailed_analysis": insight.detailed_analysis,
                "key_findings": insight.key_findings,
                "recommendations": insight.recommendations,
                "risk_level": insight.risk_level,
                "confidence_score": insight.confidence_score,
                "generated_at": insight.generated_at.isoformat(),
                "data_period": insight.data_period
            },
            "data_summary": {
                "entries_analyzed": len(entries),
                "analysis_type": insight_type,
                "ai_service": "AWS Bedrock"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.get("/ai/executive-report")
async def get_executive_report(
    limit: Optional[int] = Query(200, ge=20, le=1000, description="Number of entries to analyze")
):
    """
    Generate comprehensive executive compliance report using AI.
    
    Provides:
    - Executive summary
    - Compliance overview with metrics
    - Trend analysis
    - Risk assessment
    - Strategic action items
    """
    if not AI_ANALYTICS_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="AI Analytics service not available. Please check AWS Bedrock configuration."
        )
    
    try:
        # Get entries for analysis
        entries = PersonalEntryService.get_all_with_users(limit=limit)
        
        if len(entries) < 20:
            raise HTTPException(
                status_code=400,
                detail="Need at least 20 entries for executive report"
            )
        
        # Generate executive report
        report = await bedrock_nlp.generate_executive_report(entries)
        
        return {
            "status": "success",
            "report": {
                "executive_summary": report.executive_summary,
                "compliance_overview": report.compliance_overview,
                "trend_analysis": report.trend_analysis,
                "risk_assessment": report.risk_assessment,
                "action_items": report.action_items,
                "generated_at": report.generated_at.isoformat()
            },
            "metadata": {
                "entries_analyzed": len(entries),
                "report_type": "executive",
                "ai_service": "AWS Bedrock"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Executive report generation failed: {str(e)}")


@router.post("/ai/anomaly-analysis")
async def analyze_anomalies(
    anomalies: List[dict],
    limit: Optional[int] = Query(100, ge=10, le=500, description="Number of entries to analyze")
):
    """
    Analyze detected anomalies using AI.
    
    Provides intelligent analysis of compliance anomalies including:
    - Root cause analysis
    - Impact assessment
    - Mitigation strategies
    - Immediate actions required
    """
    if not AI_ANALYTICS_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="AI Analytics service not available. Please check AWS Bedrock configuration."
        )
    
    try:
        if not anomalies:
            raise HTTPException(
                status_code=400,
                detail="No anomalies provided for analysis"
            )
        
        # Get entries for context
        entries = PersonalEntryService.get_all_with_users(limit=limit)
        
        if len(entries) < 5:
            raise HTTPException(
                status_code=400,
                detail="Need at least 5 entries for anomaly analysis"
            )
        
        # Generate anomaly analysis
        insight = await bedrock_nlp.generate_anomaly_analysis(entries, anomalies)
        
        return {
            "status": "success",
            "analysis": {
                "type": insight.insight_type,
                "title": insight.title,
                "summary": insight.summary,
                "detailed_analysis": insight.detailed_analysis,
                "key_findings": insight.key_findings,
                "recommendations": insight.recommendations,
                "risk_level": insight.risk_level,
                "confidence_score": insight.confidence_score,
                "generated_at": insight.generated_at.isoformat(),
                "data_period": insight.data_period
            },
            "anomaly_summary": {
                "total_anomalies": len(anomalies),
                "entries_analyzed": len(entries),
                "analysis_type": "anomaly",
                "ai_service": "AWS Bedrock"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly analysis failed: {str(e)}")

@router.get("/ai/quick-insights")
async def get_quick_insights(
    limit: Optional[int] = Query(50, ge=5, le=200, description="Number of entries to analyze")
):
    """
    Get quick AI insights for dashboard display.
    
    Provides concise AI analysis suitable for dashboard widgets:
    - Brief summary
    - Key metrics
    - Top recommendations
    - Risk level
    """
    if not AI_ANALYTICS_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "AI service not available",
            "fallback_data": {
                "summary": "AI insights not available",
                "risk_level": "unknown",
                "recommendations": ["Configure AWS Bedrock for AI insights"]
            }
        }
    
    try:
        # Get recent entries
        entries = PersonalEntryService.get_all_with_users(limit=limit)
        
        if len(entries) < 5:
            return {
                "status": "insufficient_data",
                "message": "Need at least 5 entries for analysis",
                "fallback_data": {
                    "summary": "Insufficient data for analysis",
                    "risk_level": "unknown",
                    "recommendations": ["Collect more compliance data"]
                }
            }
        
        # Generate quick insights
        insight = await bedrock_nlp.generate_compliance_insights(entries, "comprehensive")
        
        return {
            "status": "success",
            "quick_insights": {
                "summary": insight.summary,
                "risk_level": insight.risk_level,
                "confidence": insight.confidence_score,
                "top_recommendations": insight.recommendations[:3],  # Top 3 only
                "key_findings": insight.key_findings[:3],  # Top 3 only
                "generated_at": insight.generated_at.isoformat()
            },
            "data_summary": {
                "entries_analyzed": len(entries),
                "analysis_type": "quick_insights"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Quick insights generation failed: {str(e)}",
            "fallback_data": {
                "summary": "Analysis failed",
                "risk_level": "unknown",
                "recommendations": ["Check AI service configuration"]
            }
        }


@router.post("/ai/custom-analysis")
async def generate_custom_analysis(
    user_prompt: str = Form(..., description="User's question or prompt for AI analysis"),
    limit: Optional[int] = Query(100, ge=10, le=500, description="Number of entries to analyze")
):
    """
    Generate AI analysis based on user's custom prompt/question.
    
    Allows users to ask specific questions about their compliance data and get
    AI-powered insights tailored to their question.
    """
    if not AI_ANALYTICS_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="AI Analytics service not available. Please check AWS Bedrock configuration."
        )
    
    try:
        if not user_prompt.strip():
            raise HTTPException(
                status_code=400,
                detail="User prompt cannot be empty"
            )
        
        # Get entries for analysis
        entries = PersonalEntryService.get_all_with_users(limit=limit)
        
        if len(entries) < 5:
            raise HTTPException(
                status_code=400,
                detail="Need at least 5 entries for AI analysis"
            )
        
        # Generate custom AI analysis
        insight = await bedrock_nlp.generate_custom_analysis(entries, user_prompt)
        
        return {
            "status": "success",
            "analysis": {
                "type": insight.insight_type,
                "title": insight.title,
                "summary": insight.summary,
                "detailed_analysis": insight.detailed_analysis,
                "key_findings": insight.key_findings,
                "recommendations": insight.recommendations,
                "risk_level": insight.risk_level,
                "confidence_score": insight.confidence_score,
                "generated_at": insight.generated_at.isoformat(),
                "data_period": insight.data_period
            },
            "user_prompt": user_prompt,
            "data_summary": {
                "entries_analyzed": len(entries),
                "analysis_type": "custom",
                "ai_service": "AWS Bedrock"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom analysis failed: {str(e)}")


@router.post("/ai/quick-answer")
async def get_quick_answer(
    question: str = Form(..., description="User's question for quick AI answer"),
    limit: Optional[int] = Query(50, ge=5, le=200, description="Number of entries to analyze")
):
    """
    Get a quick AI answer to a user's question about compliance data.
    
    Provides concise, direct answers to specific questions about compliance patterns,
    equipment violations, room performance, etc.
    """
    if not AI_ANALYTICS_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "AI service not available",
            "answer": "AI service not available. Please check AWS Bedrock configuration."
        }
    
    try:
        if not question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )
        
        # Get entries for analysis
        entries = PersonalEntryService.get_all_with_users(limit=limit)
        
        if len(entries) < 5:
            return {
                "status": "insufficient_data",
                "message": "Need at least 5 entries for analysis",
                "answer": "Insufficient data for analysis. Please collect more compliance data."
            }
        
        # Generate quick answer
        answer = await bedrock_nlp.generate_quick_answer(entries, question)
        
        return {
            "status": "success",
            "question": question,
            "answer": answer,
            "data_summary": {
                "entries_analyzed": len(entries),
                "analysis_type": "quick_answer"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "message": f"Quick answer generation failed: {str(e)}",
            "answer": f"Sorry, I couldn't process your question. Error: {str(e)}"
        }


