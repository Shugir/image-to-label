import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Label(Base):
    __tablename__ = 'labels'
    
    id = Column(Integer, primary_key=True)
    original_image_path = Column(String)
    dutch_content = Column(JSON)
    formatted_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine('sqlite:///labels.db')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def save_label(image_path, content, formatted_text):
    session = Session()
    try:
        new_label = Label(
            original_image_path=image_path,
            dutch_content=content,
            formatted_text=formatted_text
        )
        session.add(new_label)
        session.commit()
        return new_label.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_history():
    session = Session()
    try:
        return session.query(Label).all()
    finally:
        session.close()
