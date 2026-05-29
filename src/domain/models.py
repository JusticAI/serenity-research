from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class ThemeName(StrEnum):
    AI = "AI"
    DATACENTER = "Datacenter"
    PHOTONICS = "Photonics"
    OPTICS = "Optics"
    CPO = "CPO"
    NETWORKING = "Networking"
    ROBOTICS = "Robotics"
    POWER = "Power"
    SEMICONDUCTOR = "Semiconductor"
    MATERIALS = "Materials"
    MACRO = "Macro"
    PORTFOLIO = "Portfolio"
    FRAMEWORK = "Framework"
    UNKNOWN = "Unknown"


class Post(BaseModel):
    external_id: str
    created_at: datetime | None = None
    author: str = "unknown"
    text: str
    url: str | None = None
    likes: int = 0
    reposts: int = 0
    replies: int = 0
    quotes: int = 0


class TickerMention(BaseModel):
    ticker: str
    post_external_id: str


class ThemeMatch(BaseModel):
    theme: ThemeName
    post_external_id: str
    score: float = Field(ge=0)


class Thesis(BaseModel):
    summary: str
    theme: ThemeName = ThemeName.UNKNOWN
    beneficiaries: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)


class PostThesis(BaseModel):
    post_external_id: str
    summary: str
    theme: ThemeName = ThemeName.UNKNOWN
    beneficiaries: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)


class PredictionDirection(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    CONDITIONAL = "conditional"
    UNCERTAIN = "uncertain"


class Prediction(BaseModel):
    text: str
    direction: PredictionDirection = PredictionDirection.UNCERTAIN
    condition: str | None = None
    horizon: str | None = None
    confidence: float = Field(default=0.45, ge=0, le=1)
    status: str = "unreviewed"


class PostPrediction(Prediction):
    post_external_id: str


class ReportPaths(BaseModel):
    database: str
    markdown_report: str
    graph_json: str | None = None
