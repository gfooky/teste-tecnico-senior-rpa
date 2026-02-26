from contextlib import asynccontextmanager
from typing import List, Dict, Any
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db, init_db
from app.core.rabbitmq import publish_job_message
from app.models.domain import Job, JobStatus, HockeyTeam, OscarFilm
from app.schemas.schemas import JobResponse, HockeyTeamResponse, OscarFilmResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="RPA Crawler API", 
    version="1.0.0",
    lifespan=lifespan  
)


@app.post("/crawl/{target}", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_crawl_job(target: str, db: Session = Depends(get_db)) -> Job:
    if target not in ["hockey", "oscar", "all"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid target. Must be 'hockey', 'oscar', or 'all'."
        )
    
    new_job = Job(target=target, status=JobStatus.PENDING)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    await publish_job_message(job_id=new_job.id, target=target)
    
    return new_job


@app.get("/jobs", response_model=List[JobResponse])
def list_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[Job]:
    return db.query(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: UUID, db: Session = Depends(get_db)) -> Job:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return job


@app.get("/jobs/{job_id}/results")
def get_job_results(job_id: UUID, db: Session = Depends(get_db)) -> Dict[str, Any]:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    
    results = {}
    if job.target in ["hockey", "all"]:
        hockey_data = db.query(HockeyTeam).filter(HockeyTeam.job_id == job_id).all()
        results["hockey"] = [HockeyTeamResponse.model_validate(h).model_dump() for h in hockey_data]
        
    if job.target in ["oscar", "all"]:
        oscar_data = db.query(OscarFilm).filter(OscarFilm.job_id == job_id).all()
        results["oscar"] = [OscarFilmResponse.model_validate(o).model_dump() for o in oscar_data]
        
    return results


@app.get("/results/hockey", response_model=List[HockeyTeamResponse])
def get_all_hockey_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[HockeyTeam]:
    return db.query(HockeyTeam).offset(skip).limit(limit).all()


@app.get("/results/oscar", response_model=List[OscarFilmResponse])
def get_all_oscar_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[OscarFilm]:
    return db.query(OscarFilm).offset(skip).limit(limit).all()