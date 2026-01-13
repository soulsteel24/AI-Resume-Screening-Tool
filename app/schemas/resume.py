from pydantic import BaseModel
from typing import List, Optional, Dict

class MissingKeyword(BaseModel):
    keyword: str
    importance: int

class GrammarIssue(BaseModel):
    message: str
    context: str
    suggestions: List[str]

class ScoreBreakdown(BaseModel):
    keyword_match: float
    semantic_similarity: float
    skills_coverage: float
    experience_relevance: float
    grammar_score: float

class ImprovementTip(BaseModel):
    category: str
    tip: str
    priority: int  # 1 = high, 2 = medium, 3 = low

class ResumeAnalysisResponse(BaseModel):
    overall_ats_score: float
    semantic_score: float
    keyword_match_score: float
    skills_coverage_score: float
    experience_relevance_score: float
    grammar_score: float
    score_breakdown: ScoreBreakdown
    missing_keywords: List[MissingKeyword]
    detected_keywords: List[str]
    job_description_keywords: List[str]
    improvement_tips: List[ImprovementTip]
    grammar_issues: List[GrammarIssue]
