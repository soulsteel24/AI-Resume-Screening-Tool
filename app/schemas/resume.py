from pydantic import BaseModel
from typing import List, Optional

class MissingKeyword(BaseModel):
    keyword: str
    importance: int

class ResumeAnalysisResponse(BaseModel):
    semantic_score: float
    keyword_match_score: float
    missing_keywords: List[MissingKeyword]
    detected_keywords: List[str]
    job_description_keywords: List[str]
