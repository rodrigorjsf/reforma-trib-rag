from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ResponseMode(str, Enum):
    TECNICO = "TÉCNICO"
    SIMPLIFICADO = "SIMPLIFICADO"


class UserTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"


# Request Models
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    mode: ResponseMode = ResponseMode.SIMPLIFICADO
    user_id: str | None = None


# Response Models
class Citation(BaseModel):
    article: str
    section: str | None = None
    law: str
    text: str
    url: str | None = None


class Source(BaseModel):
    id: str
    title: str
    type: Literal["law", "decree", "normative"]
    url: str | None = None
    relevant_chunks: list[str] = []


class QueryResponse(BaseModel):
    id: str
    answer: str
    citations: list[Citation]
    mode: ResponseMode
    sources: list[Source]
    tokens: int
    timestamp: datetime
    warning: str | None = None


class ValidationClaim(BaseModel):
    id: str
    texto: str
    suporte: Literal["SUPPORTED", "CONTRADICTED", "UNSUPPORTED"]
    trecho_fonte: str | None = None
    citacao_status: Literal["CORRECT", "MISSING", "WRONG"]
    citacao_presente: str | None = None
    severidade: Literal["OK", "CRITICO"]


class FallbackVerification(BaseModel):
    contexto_suficiente: bool
    fallback_usado: bool
    status: Literal["PASS", "FAIL"]


class ModeVerification(BaseModel):
    modo_solicitado: ResponseMode
    linguagem_adequada: bool
    citacoes_presentes: bool
    status: Literal["PASS", "WARN"]


class ValidationResult(BaseModel):
    veredicto: Literal["PASS", "FAIL"]
    severidade: Literal["OK", "AVISO", "CRITICO"]
    claims: list[ValidationClaim]
    fallback_verificado: FallbackVerification
    modo_verificado: ModeVerification
    resumo: str


class RateLimitInfo(BaseModel):
    remaining: int
    reset_time: datetime
    daily_remaining: int | None = None


class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    tier: UserTier
    rate_limit: RateLimitInfo


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    sources_updated: datetime | None = None


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    reset_time: datetime | None = None
