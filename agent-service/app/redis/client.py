import redis
from app.core import settings
import time
client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0
)

try:
    responce = client.ping()
    print(f"Redis is running: {responce}")
except redis.ConnectionError as e:
    print(f"Error connecting to Redis: {e}")
