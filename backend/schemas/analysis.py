from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class PresignedUrlResponse(BaseModel):
    url: str
    fields: Dict[str, Any]


class AnalysisResultBase(BaseModel):
    topic: str
    summary: str | None = None
    sentiment_score: float | None = None
    review_count: int | None = None

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    id: int
    filename: str
    status: str
    created_at: datetime
    results: List[AnalysisResultBase] = []

    class Config:
        from_attributes = True