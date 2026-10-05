from typing import List, Optional
from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    thread_id: Optional[str] = "default"


class ResearchResponse(BaseModel):
    final_report: str
    research_notes: str
    analysis: str
    thread_id: str