from typing import Annotated

from fastapi import APIRouter, Depends

from fastapi import status
from app.api.dependency import get_auth_service
from app.schemas.user import UserRegister, UserResponse

from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    data: UserRegister, service: Annotated[AuthService, Depends(get_auth_service)]
):
    return await service.register(data)
