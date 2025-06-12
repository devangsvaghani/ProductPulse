from sqlalchemy import JSON, Column, Integer, String, Text, DateTime, Float, ForeignKey, func, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nickname = Column(String)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    uploads = relationship("Upload", back_populates="owner")


class Upload(Base):
    __tablename__ = 'uploads'
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), default='pending', index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship("User", back_populates="uploads")
    
    results = relationship("AnalysisResult", back_populates="upload", cascade="all, delete-orphan")


class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False, index=True)
    summary = Column(Text)
    sentiment_score = Column(Float)
    review_count = Column(Integer)
    sentiment_details = Column(JSON)
    
    upload_id = Column(Integer, ForeignKey('uploads.id'), nullable=False)
    upload = relationship("Upload", back_populates="results")