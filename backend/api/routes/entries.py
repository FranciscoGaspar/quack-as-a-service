"""
Personal entry management endpoints.
"""

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse

from database.services import UserService, PersonalEntryService
from utils.s3_uploader import upload_image_bytes_to_s3
from PIL import Image
import io

# Optional ML dependencies - import only if available
try:
    import image_detection
    ML_DEPENDENCIES_AVAILABLE = True
    print("✅ ML dependencies loaded - image detection enabled")
except ImportError as e:
    print(f"⚠️  ML dependencies not available - image detection disabled: {e}")
    print("💡 To enable image detection, install: pip install torch torchvision transformers")
    ML_DEPENDENCIES_AVAILABLE = False
from schemas import (
    PersonalEntryCreate, PersonalEntryUpdate, PersonalEntryResponse,
    PersonalEntryBaseResponse, EquipmentUpdate, SuccessResponse
)

router = APIRouter(prefix="/entries", tags=["Personal Entries"])


def _add_computed_fields(entry) -> PersonalEntryResponse:
    """Add computed fields to entry response."""
    # First validate with base schema (no computed fields)
    base_data = PersonalEntryBaseResponse.model_validate(entry)
    
    # Then create full response with computed fields
    return PersonalEntryResponse(
        **base_data.model_dump(),
        is_compliant=entry.is_compliant(),
        missing_equipment=entry.get_missing_equipment()
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


@router.get("", response_model=List[PersonalEntryResponse])
async def get_entries(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results")
):
    """Get all personal entries."""
    try:
        entries = PersonalEntryService.get_all(limit=limit)
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


@router.post("/upload-image", response_model=PersonalEntryResponse)
async def upload_image_and_analyze(
    image: UploadFile = File(..., description="Image file to analyze"),
    room_name: str = Form(..., description="Room name"),
    user_id: int = Form(..., description="User ID")
):
    """
    Upload an image, analyze it for security equipment, store in S3, and create database entry.
    
    This endpoint:
    1. Receives an image file from the frontend
    2. Analyzes the image for security equipment using AI object detection (mask, gloves, hairnet)
    3. Uploads the image to S3
    4. Creates a personal entry in the database with detected equipment
    5. Returns the standard personal entry response with compliance status
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
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")
        
        # Define detection parameters
        text_queries = "a mask. a glove. a hairnet."
        detection_threshold = 0.32
        
        # Initialize the detection model and perform analysis
        if ML_DEPENDENCIES_AVAILABLE:
            try:
                print("🤖 Initializing AI detection model...")
                image_detection.initialize_model()
                
                print(f"🔍 Analyzing image for safety equipment...")
                print(f"   Detection queries: {text_queries}")
                print(f"   Threshold: {detection_threshold}")
                
                # Perform object detection
                detection_results = image_detection.detect_objects_in_image(
                    image=pil_image,
                    text_queries=text_queries,
                    threshold=detection_threshold
                )
                
                # Analyze detection results for compliance
                required_items = ['mask', 'glove', 'hairnet']
                analysis = image_detection.analyze_detection_results(detection_results, required_items)
                
            except Exception as e:
                print(f"❌ Error during image detection: {e}")
                # Continue with empty detection results if AI fails
                analysis = {
                    'total_detected': 0,
                    'compliance_status': False,
                    'found_items': {},
                    'missing_items': ['mask', 'glove', 'hairnet']
                }
                detection_results = [{'boxes': [], 'scores': [], 'labels': []}]
        else:
            print("⚠️  Image detection skipped - ML dependencies not available")
            print("📸 Image uploaded successfully, but equipment detection is disabled")
            # Provide default values when ML is not available
            analysis = {
                'total_detected': 0,
                'compliance_status': False,  # Assume non-compliant when can't detect
                'found_items': {},
                'missing_items': ['mask', 'glove', 'hairnet']
            }
            detection_results = [{'boxes': [], 'scores': [], 'labels': []}]
        
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
            if ML_DEPENDENCIES_AVAILABLE:
                print("📸 Creating annotated image with detection boxes...")
                # Parse text_queries to get individual items for visualization
                required_items = ['mask', 'glove', 'hairnet']
                annotated_image_bytes = image_detection.create_annotated_image(
                    image=pil_image,
                    results=detection_results,
                    text_queries=required_items,
                    missing_items=analysis['missing_items']
                )
                
                # Generate filename for annotated image
                annotated_filename = f"annotated_{image.filename}" if image.filename else "annotated_image.png"
                
                # Upload annotated image to S3
                image_url = upload_image_bytes_to_s3(annotated_image_bytes, annotated_filename)
                print(f"✅ Annotated image created and uploaded successfully")
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
        
        # Create database entry
        db_entry = PersonalEntryService.create(
            user_id=user_id,
            room_name=room_name,
            equipment=equipment_detected,
            image_url=image_url
        )
        
        # Return standard personal entry response with computed fields
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
