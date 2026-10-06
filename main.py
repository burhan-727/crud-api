from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

tasks = [
    {"id": 1, "title": "Buy Milk", "done": False},
    {"id": 2, "title": "Read Book", "done": True},
    {"id": 3, "title": "Do Exercise", "done": True}
]
next_id = 4

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": exc.errors()[0]["msg"]})


class TaskCreate(BaseModel):
    title: str


@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def get_all_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreate):
    global next_id
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")
    task = {"id": next_id, "title": payload.title, "done": False}
    tasks.append(task)
    next_id += 1
    return task