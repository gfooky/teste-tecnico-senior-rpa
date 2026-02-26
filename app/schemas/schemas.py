from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import List, Optional

from app.models.domain import JobStatus


class JobBase(BaseModel):
    target: str
    status: JobStatus


class JobResponse(JobBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HockeyTeamResponse(BaseModel):
    team_name: str
    year: int
    wins: int
    losses: int
    ot_losses: Optional[int] = None
    win_percentage: float
    goals_for: int
    goals_against: int
    goal_difference: int

    model_config = ConfigDict(from_attributes=True)


class OscarFilmResponse(BaseModel):
    year: str
    title: str
    nominations: int
    awards: int
    best_picture: bool

    model_config = ConfigDict(from_attributes=True)