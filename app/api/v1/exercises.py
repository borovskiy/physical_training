import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from starlette import status

from core.dependencies import exercise_services, require_user_attrs
from db.schemas.exercise_schema import CreateExerciseSchema, ExercisePage, UpdateExerciseSchema, \
    parse_create_exercise_form
from db.schemas.paginate_schema import PaginationGet
from db.schemas.workout_schema import ExerciseFullSchema
from services.exercise_service import ExerciseServices
from utils.context import get_current_user

logger = logging.getLogger(__name__)
# /api/v1/exercise
router = APIRouter()


@router.get("/", response_model=ExercisePage, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def get_exercises(
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
        pagination: PaginationGet = Depends(PaginationGet),
        user_id: int | None = None,
):
    """
    get list exercises from DB by pagination
    """
    logger.info("Try get exercise services")
    return await exercise_serv.get_exercises(pagination.limit, pagination.start, user_id)


@router.get("/{exercise_id}", response_model=ExerciseFullSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def get_exercise_id(
        exercise_id: int,
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
):
    """
    get exercise from DB by id
    """
    logger.info("Try get exercise services")
    return await exercise_serv.get_exercise(exercise_id)


@router.post("/", response_model=ExerciseFullSchema, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_user_attrs())])
async def create_exercise(
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
        exercise_schema: CreateExerciseSchema = Depends(parse_create_exercise_form),
        file: UploadFile = File(),
        user_id: int | None = None,
):
    """
    Create new exercises in DB
    """
    logger.info("Try get exercise service")
    return await exercise_serv.create_exercise(exercise_schema, file, user_id)


@router.put("/update_exercise_data/{exercise_id}", response_model=ExerciseFullSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def update_exercise_data_by_id(
        exercise_id: int,
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
        schema: CreateExerciseSchema,
):
    """
    update data of the exercise in DB by id
    """
    logger.info("Try get exercise services")
    return await exercise_serv.update_exercise(exercise_id, schema)


@router.put("/update_exercise_file/{exercise_id}", response_model=ExerciseFullSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def update_exercise_file_admin(
        exercise_id: int,
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
        file: UploadFile = File(),
):
    """
    update file of the exercise in DB by id
    """
    logger.info("Try get exercise services")
    return await exercise_serv.update_file_exercise(exercise_id, file)


@router.delete("/{exercise_id}", response_model=ExerciseFullSchema, status_code=status.HTTP_200_OK,
               dependencies=[Depends(require_user_attrs())])
async def remove_exercises(
        exercise_id: int,
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
):
    """
    delete an exercise from the database by id. In all workouts Where this exercise was, the order will be changed
    """
    logger.info("Try get exercise services")
    return await exercise_serv.remove_exercise_from_all_workout(exercise_id)
