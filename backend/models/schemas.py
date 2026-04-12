from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any
import re

class VideoAnalyzeRequest(BaseModel):
    url: str = Field(..., min_length=10, max_length=2000)

    @validator('url')
    def validate_url(cls, v):
        # Whitelist allowed domains
        allowed_domains = [
            'youtube.com', 'youtu.be', 'tiktok.com', 'instagram.com',
            'facebook.com', 'fb.watch', 'twitter.com', 'x.com',
            'vimeo.com', 'dailymotion.com', 'threads.net'
        ]

        # Check if URL starts with http/https
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')

        # Extract domain
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', v)
        if not domain_match:
            raise ValueError('Invalid URL format')

        domain = domain_match.group(1).lower()

        # Check if domain is whitelisted
        if not any(allowed in domain for allowed in allowed_domains):
            raise ValueError(f'Domain not allowed. Allowed domains: {", ".join(allowed_domains)}')

        # Prevent SSRF to localhost/private IPs
        blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '10.', '172.16.', '192.168.', '169.254.']
        if any(blocked in domain for blocked in blocked_hosts):
            raise ValueError('URL points to private network')

        return v

class VideoResponse(BaseModel):
    id: str
    status: str
    url: str
    platform: Optional[str] = None
    title: Optional[str] = None
    analysis_result: Optional[dict] = None
    error_message: Optional[str] = None

class ChatRequest(BaseModel):
    video_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=5000)

    @validator('video_id')
    def validate_video_id(cls, v):
        # UUID format validation
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, v, re.IGNORECASE):
            raise ValueError('Invalid video ID format')
        return v

    @validator('message')
    def validate_message(cls, v):
        # Prevent control characters and null bytes
        if '\x00' in v or any(ord(c) < 32 and c not in '\n\r\t' for c in v):
            raise ValueError('Message contains invalid characters')
        return v.strip()

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
