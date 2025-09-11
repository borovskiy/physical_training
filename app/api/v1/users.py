from typing import Annotated

from fastapi import APIRouter, Depends

from core.dependencies import user_services, require_user_attrs
from db.models import User
from db.schemas.user import UserGetModelSchema, UserPostModelUpdateSchema, UserAdminPutModelSchema, \
    UserAdminGetModelSchema
from services.user_versice import UserServices

router = APIRouter()



@router.get("/me", response_model=UserGetModelSchema)
async def me(
        user_serv: Annotated[UserServices, Depends(user_services)],
        current_user: User = Depends(require_user_attrs()),
):
    return current_user


@router.put("/me", response_model=UserGetModelSchema)
async def me(
        data_user: UserPostModelUpdateSchema,
        user_serv: Annotated[UserServices, Depends(user_services)],
        current_user: User = Depends(require_user_attrs()),
):
    result = await user_serv.update_user_profile(data_user, current_user)
    return result


@router.get("/{user_id}", response_model=UserAdminGetModelSchema)
async def get_user_for_admin(
        user_id,
        user_serv: Annotated[UserServices, Depends(user_services)],
        current_user: User = Depends(require_user_attrs(is_admin=True)),
):
    result = await user_serv.find_user(user_id)
    return result


@router.put("/{user_id}", response_model=UserAdminGetModelSchema)
async def me(
        user_id,
        data_user: UserAdminPutModelSchema,
        user_serv: Annotated[UserServices, Depends(user_services)],
        current_user: User = Depends(require_user_attrs(is_admin=True)),
):
    result = await user_serv.update_user_profile_admin(user_id, data_user)
    return result
