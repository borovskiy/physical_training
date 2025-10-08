import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends
from starlette import status

from core.dependencies import require_user_attrs, workout_services
from db.schemas.paginate_schema import PaginationGet
from db.schemas.workout_schema import WorkoutExerciseCreateSchema, WorkoutFullSchema, WorkoutPage
from services.workout_service import WorkoutServices

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=WorkoutPage, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs(is_admin=True))])
async def get_workouts(
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
        pagination: PaginationGet = Depends(PaginationGet),
        user_id: int | None = None,
):
    """
    Displays all available workouts
    Including those that will be available in groups where you were invited
    """
    logger.info("Try get workout service")
    return await workout_serv.get_workouts(pagination.limit, pagination.start, user_id)


@router.get("/{workout_id}", response_model=WorkoutFullSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def get_workout(
        workout_id: int,
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
):
    """
    Displays workout by ID
    Including those that will be available in groups to which you were invited.
    """
    logger.info("Try get workout service")
    return await workout_serv.get_workout_id(workout_id)


@router.post("/", response_model=WorkoutFullSchema, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_user_attrs())])
async def create_workout(
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
        workout_schema: WorkoutExerciseCreateSchema,
        user_id: int | None = None,
):
    """
    Creates a workout with set exercise sequences
    """
    logger.info("Try get workout service")
    return await workout_serv.create_workout(workout_schema, user_id)


@router.put("/{workout_id}", response_model=WorkoutFullSchema, status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(require_user_attrs())])
async def update_workout(
        workout_id: int,
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
        workout_schema: WorkoutExerciseCreateSchema,
):
    """
    Updates a workout with set exercise sequences
    """
    logger.info("Try get workout service")
    return await workout_serv.update_workout(workout_id, workout_schema)


@router.delete("/{workout_id}", status_code=status.HTTP_200_OK,
               dependencies=[Depends(require_user_attrs())])
async def remove_workout(
        workout_id: int,
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
):
    """
    Deletes a workout
    Eliminates the connection between exercise and training.
    """
    logger.info("Try get workout service")
    return await workout_serv.remove_workout(workout_id)
