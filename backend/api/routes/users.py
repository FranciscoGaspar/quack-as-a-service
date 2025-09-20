"""
User management endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from io import BytesIO
from PIL import Image
import io

from database.services import UserService
from schemas import UserCreate, UserUpdate, UserResponse, SuccessResponse

# Optional ML dependencies for QR detection
try:
    import image_detection
    QR_DETECTION_AVAILABLE = True
    print("✅ QR detection available in users module")
except ImportError:
    QR_DETECTION_AVAILABLE = False
    print("⚠️  QR detection not available in users module")

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user."""
    try:
        db_user = UserService.create(name=user.name, qr_code=user.qr_code)
        return UserResponse.model_validate(db_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[UserResponse])
async def get_users():
    """Get all users."""
    try:
        users = UserService.get_all()
        return [UserResponse.model_validate(user) for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get a user by ID."""
    try:
        user = UserService.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/qr-code/{qr_code}", response_model=UserResponse)
async def get_user_by_qr_code(qr_code: str):
    """Get a user by QR code."""
    try:
        user = UserService.get_by_qr_code(qr_code)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate):
    """Update a user."""
    try:
        db_user = UserService.get_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        updated_user = UserService.update(user_id, name=user.name, qr_code=user.qr_code)
        return UserResponse.model_validate(updated_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(user_id: int):
    """Delete a user."""
    try:
        user = UserService.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        UserService.delete(user_id)
        return SuccessResponse(message=f"User {user_id} deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/generate-qr-code", response_model=UserResponse)
async def generate_user_qr_code(user_id: int):
    """Generate and assign a QR code to a user."""
    try:
        user = UserService.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate QR code if user doesn't have one
        if not user.qr_code:
            from datetime import datetime
            import uuid
            
            # Generate QR data
            clean_name = user.name.lower().replace(" ", "_").replace("-", "_")
            clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
            timestamp = datetime.now().strftime("%Y%m")
            unique_id = str(uuid.uuid4().hex[:8])
            qr_data = f"user_{clean_name}_{user.id}_{unique_id}_{timestamp}"
            
            # Update user
            updated_user = UserService.update(user_id, qr_code=qr_data)
            return UserResponse.model_validate(updated_user)
        
        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/qr-code-image")
async def get_user_qr_code_image(user_id: int, format: str = "png", size: int = 10):
    """Download QR code image for a user."""
    try:
        # Check if qrcode is available
        try:
            import qrcode
            from PIL import Image
        except ImportError:
            raise HTTPException(
                status_code=503, 
                detail="QR code generation not available. Install qrcode library."
            )
        
        user = UserService.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.qr_code:
            raise HTTPException(
                status_code=400, 
                detail="User has no QR code. Generate one first using POST /{user_id}/generate-qr-code"
            )
        
        # Generate QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=4,
        )
        
        qr.add_data(user.qr_code)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Return as streaming response
        return StreamingResponse(
            BytesIO(img_buffer.getvalue()),
            media_type=f"image/{format.lower()}",
            headers={
                "Content-Disposition": f"attachment; filename=user_{user_id}_qr_code.{format.lower()}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect", response_model=dict)
async def detect_user_from_qr_image(
    file: UploadFile = File(..., description="Image file to scan for QR code")
):
    """
    Detect QR codes in an image and return matching user information.
    
    This endpoint:
    1. Receives an image file
    2. Scans for QR codes in the image  
    3. Matches detected QR codes to registered users
    4. Returns user information if found
    
    Use this endpoint to identify users from QR codes in images.
    """
    try:
        # Validate image file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image bytes
        image_bytes = await file.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Convert image bytes to PIL Image
        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            # Ensure image is in RGB format
            if pil_image.mode != 'RGB':
                print(f"🔄 Converting uploaded image from {pil_image.mode} to RGB for processing")
                pil_image = pil_image.convert('RGB')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")
        
        # Detect QR codes
        print("🔍 Scanning image for QR codes...")
        qr_codes = []
        
        if QR_DETECTION_AVAILABLE:
            try:
                qr_codes = image_detection.detect_qr_codes(pil_image)
            except Exception as e:
                print(f"❌ Error during QR code detection: {e}")
                qr_codes = []
        else:
            raise HTTPException(
                status_code=503, 
                detail="QR code detection not available. Please install required dependencies."
            )
        
        # Check if any QR codes were found
        if not qr_codes:
            raise HTTPException(
                status_code=404, 
                detail="No QR code detected in image"
            )
        
        # Use the first QR code found
        first_qr = qr_codes[0]
        qr_data = first_qr['data']
        
        # Try to match QR code to user
        user = UserService.get_by_qr_code(qr_data)
        if user:
            print(f"✅ QR code matched to user: {user.name} (ID: {user.id})")
            return {
                'user_id': user.id,
                'name': user.name
            }
        else:
            print(f"⚠️  QR code '{qr_data}' not matched to any user")
            raise HTTPException(
                status_code=404, 
                detail=f"QR code detected but no matching user found: {qr_data}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in detect_user_from_qr_image: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


