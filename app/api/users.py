from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user
from app.models.user import UserORM
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users")


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(user: Annotated[UserORM, Depends(get_current_user)]) -> UserORM:
    return user
