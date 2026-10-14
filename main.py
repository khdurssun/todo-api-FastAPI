from uuid import uuid4
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
)

tasks: list[TaskReadSchema] = []


class TaskReadSchema(BaseModel):
    id: str
    title: str
    is_completed: bool


class TaskCreateSchema(BaseModel):
    title: str


@app.get("/tasks")
def get_all_task() -> list[TaskReadSchema]:
    return tasks


@app.post("/tasks")
def add_task(payload: TaskCreateSchema) -> TaskReadSchema:
    new_task = TaskReadSchema(id=str(uuid4()), title=payload.title, is_completed=False)
    tasks.append(new_task)
    return new_task
