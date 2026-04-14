# Дополнительные схемы для внутреннего использования (при необходимости)
from pydantic import BaseModel
from typing import Optional

class PatentDocument(BaseModel):
    patent_id: str
    title: str
    abstract: Optional[str] = None

class PaperDocument(BaseModel):
    paper_id: str
    title: str
    abstract: Optional[str] = None
