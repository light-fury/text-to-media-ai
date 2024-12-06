# database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from config import DB_URI

Base = declarative_base()

class UserContent(Base):
    __tablename__ = 'user_content'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False)
    prompt = Column(Text, nullable=False)
    video_paths = Column(Text, nullable=True)   # store JSON list of video paths
    image_paths = Column(Text, nullable=True)   # store JSON list of image paths
    status = Column(String(50), nullable=False, default="Processing")
    generated_at = Column(DateTime, default=datetime.utcnow)

class UserLog(Base):
    __tablename__ = 'user_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False) # 'Login', 'View Content'
    content_name = Column(String(200), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

engine = create_engine(DB_URI, echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Get a new DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_user_content(user_id, prompt):
    """Add a new user content record to the DB."""
    db = SessionLocal()
    content = UserContent(user_id=user_id, prompt=prompt, status="Processing")
    db.add(content)
    db.commit()
    db.refresh(content)
    db.close()
    return content.id

def update_user_content(content_id, image_paths, video_paths, status="Completed"):
    db = SessionLocal()
    content = db.query(UserContent).filter(UserContent.id == content_id).first()
    if content:
        content.image_paths = json.dumps(image_paths) if image_paths else None
        content.video_paths = json.dumps(video_paths) if video_paths else None
        content.status = status
        db.commit()
    db.close()

def get_user_content_by_user_id(user_id):
    db = SessionLocal()
    content = db.query(UserContent).filter(UserContent.user_id == user_id).order_by(UserContent.id.desc()).first()
    db.close()
    return content

def add_user_log(user_id, action, content_name=None):
    db = SessionLocal()
    log = UserLog(user_id=user_id, action=action, content_name=content_name)
    db.add(log)
    db.commit()
    db.close()
