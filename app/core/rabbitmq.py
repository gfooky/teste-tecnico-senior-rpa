import json
from uuid import UUID
from aio_pika import connect_robust, Message, DeliveryMode

# TODO: Mover para variáveis de ambiente (ex: pydantic-settings)
RABBITMQ_URL = "amqp://rpa_user:rpa_password@localhost:5672/"
QUEUE_NAME = "scraper_tasks"


async def publish_job_message(job_id: UUID, target: str) -> None:
    """
    Connects to RabbitMQ and publishes a job message to the queue.
    Uses robust connection and persistent delivery for fault tolerance.
    """
    connection = await connect_robust(RABBITMQ_URL)
    
    async with connection:
        channel = await connection.channel()
        
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        
        payload = {
            "job_id": str(job_id),
            "target": target
        }
        
        message = Message(
            body=json.dumps(payload).encode("utf-8"),
            delivery_mode=DeliveryMode.PERSISTENT
        )
        
        await channel.default_exchange.publish(
            message,
            routing_key=queue.name
        )