from typing import Annotated, List

from fastapi import APIRouter, Depends, File, UploadFile
from starlette import status

from core.dependencies import exercise_services, get_s3_connector, require_user_attrs
from core.s3_cloud_connector import S3CloudConnector
from db.models import User
from db.schemas.exercise import CreateExerciseSchema, ExerciseSchema, ExercisePage, UpdateExerciseSchema
from db.schemas.paginate import PaginationGet
from services.exercise_service import ExerciseServices

router = APIRouter()


@router.post("/create_exercise", response_model=ExerciseSchema, status_code=status.HTTP_201_CREATED)
async def create_exercise(
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
        current_user: User = Depends(require_user_attrs()),
        payload: CreateExerciseSchema = Depends(CreateExerciseSchema.as_form),
        file: UploadFile = File(),

):
    result = await exercise_serv.add_exercise(current_user, payload, file)
    return result


@router.get("/get_exercises", response_model=ExercisePage, status_code=status.HTTP_200_OK)
async def create_exercises(
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
        current_user: User = Depends(require_user_attrs()),
        pagination: PaginationGet = Depends(PaginationGet),
):
    result = await exercise_serv.get_exercises(current_user, pagination.limit, pagination.start)
    return result

@router.get("/get_exercise/{exercise_id}", response_model=ExerciseSchema, status_code=status.HTTP_200_OK)
async def create_exercise(
        exercise_id:int,
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
        current_user: User = Depends(require_user_attrs()),
):
    result = await exercise_serv.get_exercise(current_user, exercise_id)
    return result


@router.put("/update_exercise_data/{exercise_id}", response_model=ExerciseSchema, status_code=status.HTTP_200_OK)
async def update_exercise_data(
        exercise_id: int,
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
        schema: UpdateExerciseSchema,
        current_user: User = Depends(require_user_attrs()),
):
    result = await exercise_serv.update_exercise(exercise_id, schema, current_user)
    return result


@router.put("/update_exercise_file/{exercise_id}", response_model=ExerciseSchema, status_code=status.HTTP_200_OK)
async def update_exercise_file(
        exercise_id: int,
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
        current_user: User = Depends(require_user_attrs()),
        file: UploadFile = File(),
):
    result = await exercise_serv.update_file_exercise(current_user, exercise_id, file)
    return result
