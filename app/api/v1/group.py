import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends
from starlette import status

from core.dependencies import require_user_attrs, group_services
from db.schemas.group_schema import GroupCreateSchema, GroupFullSchema, GroupMembersCreateSchema, \
    GroupPage, GroupGetSchema, GroupMembersAddSchema, GroupGetOneSchema
from db.schemas.paginate_schema import PaginationGet
from services.group_service import GroupServices

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/", response_model=GroupPage, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def get_groups(
        group_serv: Annotated[GroupServices, Depends(group_services)],
        pagination: PaginationGet = Depends(PaginationGet),
        user_id: int | None = None,
):
    """
    Get all the groups that belong to you or that you are a member of
    """
    logger.info("Try get group service")
    return await group_serv.get_groups_user(pagination.limit, pagination.start, user_id)


@router.get("/{group_id}", response_model=GroupGetSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def get_group_id(
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
):
    """
    Get the group by group ID that belongs to you.
    """
    logger.info("Try get group service")
    return await group_serv.get_group_by_id(group_id)


@router.post("/", response_model=GroupGetOneSchema, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_user_attrs())])
async def create_group(
        group_serv: Annotated[GroupServices, Depends(group_services)],
        group_schema: GroupCreateSchema,
        user_id: int | None = None,
):
    """
    Create group.
    """
    logger.info("Try get group service")
    return await group_serv.create_group(group_schema, user_id)


@router.put("/rename_group/{group_id}", response_model=GroupGetOneSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def rename_group(
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
        group_schema: GroupCreateSchema,
):
    """
    Rename group name.
    """
    logger.info("Try get group service")
    return await group_serv.rename_group(group_id, group_schema.name)


@router.put("/add_members_in_group/{group_id}", response_model=GroupGetSchema,
            status_code=status.HTTP_200_OK, dependencies=[Depends(require_user_attrs())])
async def add_members_in_group(
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
        members_schema: List[GroupMembersAddSchema],
        user_id: int | None = None,
):
    """
    Add a member to a group
    Will open access to a workout that will be linked to the group
    """
    logger.info("Try get group service")
    return await group_serv.add_members_in_group(group_id, members_schema, user_id)


@router.put("/add_workout_in_group/{workout_id}/{group_id}", response_model=GroupGetSchema,
            status_code=status.HTTP_200_OK, dependencies=[Depends(require_user_attrs())])
async def add_workout_in_group(
        workout_id: int,
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
        user_id: int | None = None,
):
    """
    Add workout to group
    The workout will be available to all group members
    """
    logger.info("Try get group service")
    return await group_serv.add_workout_in_group(group_id, workout_id, user_id)


@router.delete("/remove_members_from_group/{member_id}/{group_id}", response_model=GroupGetOneSchema,
               status_code=status.HTTP_201_CREATED,
               dependencies=[Depends(require_user_attrs())])
async def remove_members_from_group(
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
        members_schema: List[GroupMembersAddSchema],
):
    """
    Removes a member from a group.
    Workout associated with this group will no longer be available to him.
    """
    logger.info("Try get group service")
    return await group_serv.delete_members(members_schema, group_id)


@router.delete("/remove_workout_from_group/{workout_id}/{group_id}", status_code=status.HTTP_200_OK,
               dependencies=[Depends(require_user_attrs())])
async def remove_workout_from_group(
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
):
    """
    Removes a workout from the group. its members will not be able to see it in their list of available workouts.
    """
    logger.info("Try get group service")
    return await group_serv.delete_workout_from_group(group_id)


@router.delete("/delete_group/{group_id}", status_code=status.HTTP_200_OK,
               dependencies=[Depends(require_user_attrs())])
async def delete_group(
        group_id: int,
        group_serv: Annotated[GroupServices, Depends(group_services)],
):
    """
    Remove group.
    deletes the group and all users associated with it
    Access to workout classes will also be lost.
    """
    logger.info("Try get group service")
    return await group_serv.delete_group(group_id)
