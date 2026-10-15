from typing import Optional

from pydantic import BaseModel


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
    role: str
    created_at: str


class UserWithProfileResponse(BaseModel):
    user: UserResponse
    profile: ProfileResponse


class AuthMeResponse(BaseModel):
    id: str
    email: str
    role: str
    profile: Optional[ProfileResponse] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class MessageResponse(BaseModel):
    message: str


class IncidentSummaryResponse(BaseModel):
    total: int
    by_status: dict[str, int]
    by_category: dict[str, int]
    by_origin: dict[str, int]
    by_branch: dict[str, int]


class IncidentAnalysisResponse(BaseModel):
    total_records: int
    valid_records: int
    invalid_records: int
    error_counts: dict[str, int]
    category_counts: dict[str, int]
    status_counts: dict[str, int]
    scored_cases: int
    closed_cases: int
    average_score: float
    score_counts: dict[int, int]