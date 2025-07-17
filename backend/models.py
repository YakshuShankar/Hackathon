from sqlalchemy import Column, Integer, String, Date, Time
from database import Base

class Operators(Base):
    __tablename__ = "operators"
    operator_id = Column(String(50), primary_key=True, index=True)
    password = Column(String(100))

class TaskDetails(Base):
    __tablename__ = "task_details"
    task_id = Column(String(50), primary_key=True, index=True)
    operator_id = Column(String(50))
    task = Column(String(50))
    date = Column(Date)
    status=Column(String(50))
    time_started = Column(Time)
    task_estimation = Column(Integer)

class MachineDetails(Base):
    __tablename__="machine_details"
    machine_id=Column(Integer,autoincrement=True, primary_key=True, index=True)
    seat_belt_status=Column(String(10))
    cabin_door_access=Column(String(10))
    fuel_level=Column(Integer)
    

