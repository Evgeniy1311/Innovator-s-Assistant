from pydantic import BaseModel, Field
from typing import List, Optional

class UserRequest(BaseModel):
    free_text_interests: str = Field(..., description="Свободное описание научных интересов")
    domains: List[str] = Field(default=[], description="Научные области (напр. AI, Biology)")
    skills: List[str] = Field(default=[], description="Ключевые навыки")
    experience_years: Optional[int] = Field(None, description="Опыт в годах")
    education_level: Optional[str] = Field(None, description="Уровень образования")

class HypothesisIdea(BaseModel):
    title: str
    description: str
    novelty_aspect: str
    feasibility_assessment: str

class ValidationResult(BaseModel):
    query_used: str
    similar_patents_count: int
    similar_papers_count: int
    novelty_score: str  # "High", "Medium", "Low"
    risks: str
    top_references: List[str]

class FinalReport(BaseModel):
    user_context_summary: str
    generated_hypotheses: List[HypothesisIdea]
    validation_report: List[ValidationResult]
