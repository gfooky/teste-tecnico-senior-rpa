from fastapi import status


def test_create_crawl_job_success(client):
    """Tests if the API accepts a valid target and creates the job as PENDING."""
    response = client.post("/crawl/hockey")
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    
    data = response.json()
    assert data["target"] == "hockey"
    assert data["status"] == "pending"
    assert "id" in data
    assert "created_at" in data


def test_create_crawl_job_invalid_target(client):
    """Tests if the API blocks targets that don't exist (error validation)."""
    response = client.post("/crawl/futebol")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid target" in response.json()["detail"]


def test_get_jobs_empty(client):
    """Tests the listing of jobs when the database is empty."""
    response = client.get("/jobs")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_job_not_found(client):
    """Tests the search for a job that doesn't exist in the database."""
    fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/jobs/{fake_uuid}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Job not found."