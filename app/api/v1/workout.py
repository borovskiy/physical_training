import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends
from starlette import status

from app.core.dependencies import require_user_attrs, workout_services
from app.db.schemas.paginate_schema import PaginationGet
from app.db.schemas.workout_schema import WorkoutCreateSchema, WorkoutExerciseCreateSchema, WorkoutFullSchema, \
    WorkoutPage
from app.services.workout_service import WorkoutServices

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/get_workouts", response_model=WorkoutPage, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def get_workouts(
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
        pagination: PaginationGet = Depends(PaginationGet),
):
    logger.info("Try get workout service")
    return await workout_serv.get_workouts(pagination.limit, pagination.start)


@router.get("/{workout_id}", response_model=WorkoutFullSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def get_workout(
        workout_id: int,
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
):
    logger.info("Try get workout service")
    return await workout_serv.get_workout_id(workout_id)


@router.post("/create_workout", response_model=WorkoutFullSchema, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_user_attrs())])
async def create_workout(
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
        workout_schema: WorkoutExerciseCreateSchema,
):
    logger.info("Try get workout service")
    return await workout_serv.create_workout(workout_schema)


@router.put("/update_workout/{workout_id}", response_model=WorkoutFullSchema, status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(require_user_attrs())])
async def create_workout(
        workout_id: int,
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
        workout_schema: WorkoutExerciseCreateSchema,
):
    logger.info("Try get workout service")
    return await workout_serv.update_workout(workout_id, workout_schema)


@router.delete("/{workout_id}", response_model=WorkoutExerciseCreateSchema, status_code=status.HTTP_200_OK,
               dependencies=[Depends(require_user_attrs())])
async def remove_workout(
        workout_id: int,
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
):
    logger.info("Try get workout service")
    return await workout_serv.remove_workout(workout_id)
