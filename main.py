from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

tasks = [
    {"id": 1, "title": "Buy Milk", "done": False},
    {"id": 2, "title": "Read Book", "done": True},
    {"id": 3, "title": "Do Exercise", "done": True},
]
next_id = 4

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400, content={"error": exc.errors()[0]["msg"]}
    )


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/", summary="Root status", description="Returns API information and available endpoints.")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check", description="Checks if the API server is up and running.")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks", description="Retrieve a list of all existing tasks.")
def get_all_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get task by ID", description="Retrieve details for a single task using its unique ID.")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.post("/tasks", status_code=201, summary="Create a new task", description="Add a new task with a title. Sets 'done' status to False by default.")
def create_task(payload: TaskCreate):
    global next_id
    if not payload.title.strip():
        raise HTTPException(
            status_code=400, detail="title is required and cannot be empty"
        )
    task = {"id": next_id, "title": payload.title, "done": False}
    tasks.append(task)
    next_id += 1
    return task


@app.put("/tasks/{task_id}", summary="Update a task", description="Update the title or completion status of an existing task by ID.")
def update_task(task_id: int, payload: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            if payload.title is not None:
                if not payload.title.strip():
                    raise HTTPException(
                        status_code=400, detail="title cannot be empty"
                    )
                task["title"] = payload.title
            if payload.done is not None:
                task["done"] = payload.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task", description="Remove a task permanently by ID.")
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")