import random
import redis
from celery import shared_task

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

@shared_task
def send_otp(mobile):
    otp = str(random.randint(100000, 999999))
    redis_client.setex(f"otp:{mobile}", 300, otp)  # OTP expires in 5 minutes
    print(f"OTP for {mobile}: {otp}")  # Simulate SMS (Replace with actual SMS API)
    return otp

def verify_otp(mobile, otp):
    stored_otp = redis_client.get(f"otp:{mobile}")
    if stored_otp and stored_otp == otp:
        redis_client.delete(f"otp:{mobile}")  # Remove OTP after verification
        return True
    return False

