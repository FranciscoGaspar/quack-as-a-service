"""
User management endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException

from database.services import UserService
from schemas import UserCreate, UserUpdate, UserResponse, SuccessResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user."""
    try:
        db_user = UserService.create(name=user.name)
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


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate):
    """Update a user."""
    try:
        db_user = UserService.get_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        updated_user = UserService.update(user_id, name=user.name)
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
