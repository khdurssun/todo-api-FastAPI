from uuid import uuid4
from fastapi import FastAPI, status, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, Session
from contextlib import asynccontextmanager

DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres"
engine = create_engine(DATABASE_URL)
Sessionlocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))

class TaskORM(Base):
    __tablename__ = "tasks"

    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
)


def get_db():
    db = Sessionlocal()
    try:
        yield db 
    finally:
        db.close()

def task_orm_to_model(task_orm: TaskORM) -> TaskReadSchema:
    return TaskReadSchema(id=task_orm.id, title=task_orm.title, completed=task_orm.completed)


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
def get_all_task(db: Session = Depends(get_db)) -> list[TaskReadSchema]:
    task_from_db = db.scalars(Select(TaskORM)).all()
    return [task_orm_to_model(task) for task in task_from_db]


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def add_task(payload: TaskCreateSchema, db: Session = Depends(get_db)) -> TaskReadSchema:
    new_task = TaskORM(title=payload.title, completed=False)
    db.add(new_task)
    db.commit()

    return task_orm_to_model(new_task)

@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdateSchema, db: Session = Depends(get_db)) -> TaskReadSchema:
    task_for_update = db.get(TaskORM, task_id)

    if payload.title is not None:
        task_for_update.title = payload.title
    if payload.completed is not None:
        task_for_update.completed = payload.completed

    db.commit()

    return task_for_update

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task_for_delete = db.get(TaskORM, task_id)
    db.delete(task_for_delete)
    db.commit()

    return task_for_delete   