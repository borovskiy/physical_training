from typing import Annotated, List

from fastapi import APIRouter, Depends
from starlette import status

from core.dependencies import require_user_attrs, workout_services
from db.schemas.paginate import PaginationGet
from db.schemas.workout import WorkoutCreateSchema, WorkoutExerciseCreateSchema, WorkoutFullSchema, \
    WorkoutPage
from services.workout_service import WorkoutServices

router = APIRouter()

@router.get("/get_workouts", response_model=WorkoutPage, status_code=status.HTTP_200_OK, dependencies=[Depends(require_user_attrs())])
async def get_workouts(
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
        pagination: PaginationGet = Depends(PaginationGet),
):
    result = await workout_serv.get_workouts(pagination.limit, pagination.start)
    return result

@router.get("/get_workouts_me", response_model=WorkoutPage, status_code=status.HTTP_200_OK, dependencies=[Depends(require_user_attrs())])
async def get_workouts(
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
        pagination: PaginationGet = Depends(PaginationGet),
):
    result = await workout_serv.get_workouts(pagination.limit, pagination.start)
    return result

@router.get("/{workout_id}", response_model=WorkoutFullSchema, status_code=status.HTTP_200_OK, dependencies=[Depends(require_user_attrs())])
async def get_workout(
        workout_id: int,
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
):
    result = await workout_serv.get_workout(workout_id)
    return result


@router.post("/create_workout", response_model=WorkoutFullSchema, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_user_attrs())])
async def create_workout(
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
        workout_schema: WorkoutCreateSchema,
        exercises_schema: List[WorkoutExerciseCreateSchema],
):
    result = await workout_serv.create_workout(workout_schema, exercises_schema)
    return result


@router.delete("/{workout_id}", response_model=WorkoutExerciseCreateSchema, status_code=status.HTTP_200_OK, dependencies=[Depends(require_user_attrs())])
async def remove_workout(
        workout_id: int,
        workout_serv: Annotated[WorkoutServices, Depends(workout_services)],
):
    result = await workout_serv.remove_workout(workout_id)
    return result