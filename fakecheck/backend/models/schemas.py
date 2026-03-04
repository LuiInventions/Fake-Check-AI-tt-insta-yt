from pydantic import BaseModel
from typing import List, Optional, Any

class VideoAnalyzeRequest(BaseModel):
    url: str

class VideoResponse(BaseModel):
    id: str
    status: str
    url: str
    platform: Optional[str] = None
    title: Optional[str] = None
    analysis_result: Optional[dict] = None
    error_message: Optional[str] = None

class ChatRequest(BaseModel):
    video_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    
class ClaimAssessment(BaseModel):
    claim: str
    assessment: str
    explanation: str

class AnalysisResult(BaseModel):
    fake_score: float
    verdict: str
    summary: str
    what_actually_happened: str
    claims: List[ClaimAssessment]
    sources: List[str] = []
    red_flags: List[str]
    visual_text_match: bool
    visual_analysis: str
