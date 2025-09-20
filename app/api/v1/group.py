from typing import Annotated, List

from fastapi import APIRouter, Depends
from starlette import status

from core.dependencies import require_user_attrs, group_services
from db.schemas.group_schema import GroupCreateSchema, GroupFullSchema, GroupMembersCreateSchema, \
    GroupPage, GroupGetSchema, GroupMembersAddSchema, GroupGetOneSchema
from db.schemas.paginate_schema import PaginationGet

from services.group_service import GroupServices

router = APIRouter()


@router.get("/get_groups", response_model=GroupPage, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def get_groups(
        group_serv: Annotated[GroupServices, Depends(group_services)],
        pagination: PaginationGet = Depends(PaginationGet),

):
    return await group_serv.get_groups_user(pagination.limit, pagination.start)


@router.get("/get_groups/{group_id}", response_model=GroupGetSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def get_group_id(
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
):
    return await group_serv.get_group_by_id(group_id)


@router.post("/create_group", response_model=GroupGetOneSchema, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_user_attrs())])
async def create_group(
        group_serv: Annotated[GroupServices, Depends(group_services)],
        group_schema: GroupCreateSchema,
):
    return await group_serv.create_group(group_schema)


@router.put("/rename_group/{group_id}", response_model=GroupGetOneSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def rename_group(
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
        group_schema: GroupCreateSchema,
):
    return await group_serv.rename_group(group_id, group_schema.name)


@router.delete("/delete_group/{group_id}", response_model=GroupFullSchema, status_code=status.HTTP_200_OK,
               dependencies=[Depends(require_user_attrs())])
async def delete_group(
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
):
    return await group_serv.delete_group(group_id)


@router.post("/add_members_in_group/{group_id}", response_model=List[GroupMembersCreateSchema],
             status_code=status.HTTP_200_OK, dependencies=[Depends(require_user_attrs())])
async def add_members_in_group(
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
        members_schema: List[GroupMembersAddSchema],
):
    return await group_serv.add_members_in_group(group_id, members_schema)


@router.delete("/remove_members_from_group/{member_id}/{group_id}", status_code=status.HTTP_201_CREATED,
               dependencies=[Depends(require_user_attrs())])
async def remove_members_from_group(
        member_id: int,
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
):
    return await group_serv.delete_member(member_id, group_id)


@router.delete("/remove_workout_from_group/{workout_id}/{group_id}", status_code=status.HTTP_200_OK,
               dependencies=[Depends(require_user_attrs())])
async def remove_workout_from_group(
        workout_id: int,
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
):
    return await group_serv.delete_workout_from_group(workout_id, group_id)


@router.put("/add_workout_in_group/{workout_id}/{group_id}", response_model=List[GroupMembersCreateSchema],
            status_code=status.HTTP_200_OK, dependencies=[Depends(require_user_attrs())])
async def add_workout_in_group(
        workout_id: int,
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
):
    return await group_serv.add_workout_in_group(group_id, workout_id)
