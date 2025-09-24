from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from starlette import status

from core.dependencies import exercise_services, require_user_attrs
from db.schemas.exercise_schema import CreateExerciseSchema, ExerciseSchema, ExercisePage, UpdateExerciseSchema
from db.schemas.paginate_schema import PaginationGet
from services.exercise_service import ExerciseServices

# /api/v1/exercise
router = APIRouter()


@router.post("/create_exercise", response_model=ExerciseSchema, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_user_attrs())])
async def create_exercise(
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
        exercise_schema: CreateExerciseSchema = Depends(CreateExerciseSchema.as_form),
        file: UploadFile = File(),
):
    return await exercise_serv.add_exercise(exercise_schema, file)


@router.get("/get_exercises", response_model=ExercisePage, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def get_exercises(
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
        pagination: PaginationGet = Depends(PaginationGet),
):
    return await exercise_serv.get_exercises(pagination.limit, pagination.start)


@router.get("/get_exercise/{exercise_id}", response_model=ExerciseSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def create_exercise(
        exercise_id: int,
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
):
    return await exercise_serv.get_exercise(exercise_id)


@router.put("/update_exercise_data/{exercise_id}", response_model=ExerciseSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def update_exercise_data(
        exercise_id: int,
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
        schema: UpdateExerciseSchema,
):
    result = await exercise_serv.update_exercise(exercise_id, schema)
    return result


@router.put("/update_exercise_file/{exercise_id}", response_model=ExerciseSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(require_user_attrs())])
async def update_exercise_file(
        exercise_id: int,
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
        file: UploadFile = File(),
):
    result = await exercise_serv.update_file_exercise(exercise_id, file)
    return result


@router.delete("/{exercise_id}", response_model=ExerciseSchema, status_code=status.HTTP_200_OK,
               dependencies=[Depends(require_user_attrs())])
async def remove_exercises(
        exercise_id: int,
        exercise_serv: Annotated[ExerciseServices, Depends(exercise_services)],
):
    result = await exercise_serv.remove_exercise_from_all_workout(exercise_id)
    return result
