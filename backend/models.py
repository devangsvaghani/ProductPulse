from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, func
from sqlalchemy.orm import relationship, declarative_base

# Define the Base class right here in the models file
Base = declarative_base()

class Upload(Base):
    __tablename__ = 'uploads'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), default='pending', index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    results = relationship("AnalysisResult", back_populates="upload")

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False, index=True)
    summary = Column(Text)
    sentiment = Column(String(50))
    sentiment_score = Column(Float)
    roadmap_json = Column(JSON)
    upload_id = Column(Integer, ForeignKey('uploads.id'), nullable=False)
    upload = relationship("Upload", back_populates="results")