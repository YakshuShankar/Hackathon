from fastapi import FastAPI,Body, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime,date
import models
from database import engine, SessionLocal
from sqlalchemy import or_

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/login")
def login(operator_id: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    operator = db.query(models.Operators).filter(models.Operators.operator_id == operator_id).filter( models.Operators.password==password).first()
    if not operator:
        raise HTTPException(status_code=401, detail="Invalid operator ID or password")
    return {"operator_id": operator.operator_id, "message": "Login successful"}

@app.get("/dashboard")
def dashboard(operator_id: str, db: Session = Depends(get_db)):
    operator = db.query(models.Operators).filter(models.Operators.operator_id == operator_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    tasks = db.query(models.TaskDetails).filter(
        models.TaskDetails.operator_id == operator_id,
    or_(
        models.TaskDetails.status == "in progress",
        models.TaskDetails.status == "not started"
    )
    ).all()

    return [
        {
            "task_id": task.task_id,
            "task": task.task,
            "date": task.date,
            "timestarted": task.time_started,  
            "task_estimation": task.task_estimation
        }
        for task in tasks
    ]

@app.get('/machines')
def get_machine_status(machine_id: int,db: Session = Depends(get_db)):
    machine=db.query(models.MachineDetails).filter(models.MachineDetails.machine_id==machine_id).first()
    if machine is None:
        raise HTTPException(status_code=404,detail="Machine not found")
    else:
        return {
            "seat_belt_status":machine.seat_belt_status,
            "cabin_door_access":machine.cabin_door_access,
            "fuel_level":machine.fuel_level,
        }
    
@app.put("/task/update_status")
def update_task_status(operator_id: str = Body(...), task_id: str = Body(...), db: Session = Depends(get_db)):
    task = db.query(models.TaskDetails).filter(
        models.TaskDetails.operator_id == operator_id,
        models.TaskDetails.task_id == task_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status == "not started":
        task.status = "in progress"
        task.time_started = datetime.now()
    elif task.status == "in progress":
        task.status = "completed"
    else:
        return {"message": f"Task is already '{task.status}'."}

    db.commit()
    db.refresh(task)

    return {
        "task_id": task.task_id,
        "new_status": task.status,
        "message": "Task status updated successfully"
    }

app.mount("/music", StaticFiles(directory="music"), name="music")

songs = [
{
    "title": "Song One",
    "artist": "Artist A",
    "url": "http://localhost:8000/music/song1.mp3"
},
{
    "title": "Song Two",
    "artist": "Artist B",
    "url": "http://localhost:8000/music/song2.mp3"
},
{
    "title": "Song Three",
    "artist": "Artist C",
    "url": "http://localhost:8000/music/song3.mp3"
}
]

@app.get("/songs")
def get_song_list():
return songs

