from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('sqlite:///todo.db')

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "task"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String(500))
    difficulty = Column(Integer)
    rot = Column(Integer)
    project = Column(String)
    due_date  = Column(String)
    create_date = Column(String)
    done_date = Column(String)
    status = Column(String)

Base.metadata.create_all(engine)
