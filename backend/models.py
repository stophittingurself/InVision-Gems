from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Recommendation(str, Enum):
    STRONG = "STRONG"
    CONSIDER = "CONSIDER"
    PASS = "PASS"


class CandidateInput(BaseModel):
    name: str
    age: int = Field(ge=14, le=35)
    essay: str = Field(min_length=50, description="Personal essay / free text")
    achievements: list[str] = Field(default_factory=list)
    motivation_letter: str = Field(min_length=50)
    extra_activities: list[str] = Field(default_factory=list)


class DimensionScore(BaseModel):
    score: float = Field(ge=0, le=10)
    reasoning: str


class ScoringResult(BaseModel):
    candidate_name: str
    scores: dict[str, DimensionScore]
    overall_score: float = Field(ge=0, le=10)
    recommendation: Recommendation
    summary: str
    ai_content_flag: bool
    ai_content_note: Optional[str] = None


class BatchScoringResult(BaseModel):
    shortlist: list[ScoringResult]
    total_evaluated: int
