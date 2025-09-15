from fastapi import FastAPI
from sqlalchemy.orm import configure_mappers

from app.api.v1 import auth, users, exercises, workout
import uvicorn
from dotenv import load_dotenv


def create_app() -> FastAPI:
    app = FastAPI(title="FitnessApp API", version="0.1.0")
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(exercises.router, prefix="/api/v1/exercise", tags=["exercises"])
    app.include_router(workout.router, prefix="/api/v1/workout", tags=["workouts"])

    return app


app = create_app()

if __name__ == "__main__":
    configure_mappers()

    load_dotenv()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
