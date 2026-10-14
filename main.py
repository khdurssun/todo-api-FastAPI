from uuid import uuid4
from fastapi import FastAPI, status
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
    completed: bool


class TaskCreateSchema(BaseModel):
    title: str

class TaskUpdateSchema(BaseModel):
    title: str | None = None 
    completed: bool | None = None 


@app.get("/tasks")
def get_all_task() -> list[TaskReadSchema]:
    return tasks


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def add_task(payload: TaskCreateSchema) -> TaskReadSchema:
    new_task = TaskReadSchema(id=str(uuid4()), title=payload.title, completed=False)
    tasks.append(new_task)
    return new_task

@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdateSchema):
    for task in tasks:
        if task.id == task_id:
            if payload.title is not None:
                task.title = payload.title 
            if payload.completed is not None:
                task.completed = payload.completed

            return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)