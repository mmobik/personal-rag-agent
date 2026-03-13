import redis

client = redis.Redis(
    host="localhost",
    port=6379,
    db=0
)

try:
    responce = client.ping()
    print(f"Redis is running: {responce}")
except redis.ConnectionError as e:
    print(f"Error connecting to Redis: {e}")