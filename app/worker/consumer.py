import asyncio
import json
import logging
from uuid import UUID

from aio_pika import connect_robust, IncomingMessage
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.rabbitmq import RABBITMQ_URL, QUEUE_NAME
from app.models.domain import Job, JobStatus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("worker")


async def process_message(message: IncomingMessage) -> None:
    """
    Callback function that processes a single message from the queue.
    """
    async with message.process():
        payload = json.loads(message.body.decode("utf-8"))
        job_id = UUID(payload["job_id"])
        target = payload["target"]
        
        logger.info(f"Picked up Job {job_id} for target '{target}'")
        
        db: Session = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                logger.error(f"Job {job_id} not found in DB.")
                return
            
            job.status = JobStatus.RUNNING
            db.commit()
            logger.info(f"Job {job_id} is now RUNNING")

            logger.info(f"Simulating scraping for {target}... (takes 5 seconds)")
            await asyncio.sleep(5) 

            job.status = JobStatus.COMPLETED
            db.commit()
            logger.info(f"Job {job_id} is now COMPLETED")

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            db.rollback()
            if 'job' in locals() and job:
                job.status = JobStatus.FAILED
                db.commit()
            raise e  
        finally:
            db.close()


async def main() -> None:
    """Starts the RabbitMQ consumer."""
    connection = await connect_robust(RABBITMQ_URL)
    
    async with connection:
        channel = await connection.channel()
        
        await channel.set_qos(prefetch_count=1)
        
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        
        logger.info("Worker started. Waiting for messages...")
        
        await queue.consume(process_message)
        
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())