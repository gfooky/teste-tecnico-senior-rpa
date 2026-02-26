import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Enumeração para o status do Job
class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target = Column(String, nullable=False) # 'hockey', 'oscar' ou 'all'
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos para facilitar a busca dos resultados depois
    hockey_results = relationship("HockeyTeam", back_populates="job")
    oscar_results = relationship("OscarFilm", back_populates="job")

class HockeyTeam(Base):
    __tablename__ = "hockey_teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    team_name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    wins = Column(Integer, nullable=False)
    losses = Column(Integer, nullable=False)
    ot_losses = Column(Integer, nullable=True)
    win_percentage = Column(Float, nullable=False)
    goals_for = Column(Integer, nullable=False)
    goals_against = Column(Integer, nullable=False)
    goal_difference = Column(Integer, nullable=False)

    job = relationship("Job", back_populates="hockey_results")

class OscarFilm(Base):
    __tablename__ = "oscar_films"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    year = Column(String, nullable=False)
    title = Column(String, nullable=False)
    nominations = Column(Integer, nullable=False)
    awards = Column(Integer, nullable=False)
    best_picture = Column(Boolean, nullable=False)

    job = relationship("Job", back_populates="oscar_results")