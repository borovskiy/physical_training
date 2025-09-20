from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from core.dependencies import user_services, require_user_attrs
from db.schemas.user_schema import UserGetModelSchema, UserPostModelUpdateSchema, UserAdminPutModelSchema, \
    UserAdminGetModelSchema
from services.user_versice import UserServices
from utils.context import get_current_user
from utils.create_data_db import create_db_data

# /api/v1/users/profile
router = APIRouter()


@router.get("/create_db_data")
async def me():
    await create_db_data()
    return None


@router.get("/me", response_model=UserGetModelSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def me_get(
        user_serv: Annotated[UserServices, Depends(user_services)],
):
    current_user = get_current_user()
    return current_user


@router.put("/me", response_model=UserGetModelSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def me_put(
        data_user: UserPostModelUpdateSchema,
        user_serv: Annotated[UserServices, Depends(user_services)],
):
    result = await user_serv.update_user_profile(data_user)
    return result


@router.get("/{user_id}", response_model=UserAdminGetModelSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs(is_admin=True))])
async def get_user_id_for_admin(
        user_id,
        user_serv: Annotated[UserServices, Depends(user_services)],
):
    return await user_serv.find_user(user_id)


@router.put("/{user_id}", response_model=UserAdminPutModelSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs(is_admin=True))])
async def put_user_id_for_admin(
        user_id,
        data_user: UserAdminPutModelSchema,
        user_serv: Annotated[UserServices, Depends(user_services)],
):
    result = await user_serv.update_user_admin(user_id, data_user)
    return result


@router.delete("/{user_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(require_user_attrs(is_admin=True))])
async def delete_user_id_for_admin(
        user_id: int,
        user_serv: Annotated[UserServices, Depends(user_services)],
):
    return await user_serv.remove_user(user_id)
