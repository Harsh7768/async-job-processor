import json
from fastapi import FastAPI
from pydantic import BaseModel
from app.db import get_connection

app = FastAPI()


# Request model
class JobCreate(BaseModel):
    type: str
    payload: dict
    idempotency_key: str

    class Config:
        json_schema_extra = {
            "example": {
                "type": "email",
                "payload": {
                    "to": "test@example.com"
                },
                "idempotency_key": "abc123"
            }
        }


# Create job endpoint
@app.post("/jobs")
def create_job(job: JobCreate):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Prevent duplicate job creation using idempotency key
        cur.execute(
            "SELECT id, status FROM jobs WHERE idempotency_key = %s;",
            (job.idempotency_key,)
        )
        existing = cur.fetchone()

        if existing:
            return {
                "job_id": existing[0],
                "status": existing[1],
                "message": "Duplicate request - returning existing job"
            }

        # Insert new job
        cur.execute(
            """
            INSERT INTO jobs (type, payload, status, idempotency_key)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """,
            (job.type, json.dumps(job.payload), "pending", job.idempotency_key)
        )

        job_id = cur.fetchone()[0]
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cur.close()
        conn.close()

    return {
        "job_id": job_id,
        "status": "pending"
    }



@app.post("/jobs/process")
def process_job():
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Safely pick a job using row-level locking to avoid duplicate processing
        cur.execute(
            """
            SELECT id, type, payload
            FROM jobs
            WHERE status IN ('pending', 'failed')
            AND next_run_at <= CURRENT_TIMESTAMP
            AND attempts < 3
            ORDER BY created_at
            FOR UPDATE SKIP LOCKED
            LIMIT 1;
            """
        )

        job = cur.fetchone()

        if not job:
            return {"message": "No jobs available"}

        job_id, job_type, payload = job

        # Mark job as processing
        cur.execute(
            "UPDATE jobs SET status = 'processing' WHERE id = %s;",
            (job_id,)
        )
        conn.commit()

        # Simulate processing
        print(f"[WORKER] Processing job {job_id} of type {job_type}")

        # Mark as completed
        cur.execute(
            "UPDATE jobs SET status = 'completed' WHERE id = %s;",
            (job_id,)
        )
        conn.commit()

    except Exception as e:
        conn.rollback()

        # Retry failed jobs with delay (backoff) and limited attempts
        if 'job_id' in locals():
            cur.execute(
                """
                UPDATE jobs
                SET 
                    status = 'failed',
                    attempts = attempts + 1,
                    next_run_at = CURRENT_TIMESTAMP + INTERVAL '10 seconds'
                WHERE id = %s;
                """,
                (job_id,)
            )
            conn.commit()

        raise e

    finally:
        cur.close()
        conn.close()

    return {
        "job_id": job_id,
        "status": "completed"
    }