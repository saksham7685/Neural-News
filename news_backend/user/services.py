import random
from django.core.cache import cache
import redis
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

class JwtService:
    @staticmethod
    def create_jwt(user):
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        access['uuid'] = str(user.uuid) 
        access["app_id"] = str(user.app_id) 
        
        refresh["uuid"] = str(user.uuid)  # Ensure it's stored as a string
        refresh["app_id"] = str(user.app_id)
        
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

class OtpService:
    @staticmethod
    def generate_otp(mobile):
        otp = str(random.randint(100000, 999999))
        redis_client.set(mobile, otp, ex=300)  # Set OTP with a 5-minute expiration
        return otp

    @staticmethod
    def verify_otp(mobile, otp):
        stored_otp = redis_client.get(mobile)
        if stored_otp and stored_otp.decode() == otp:
            redis_client.delete(mobile)
            return True
        return False