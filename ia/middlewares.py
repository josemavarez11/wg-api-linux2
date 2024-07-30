# your_app_name/middleware.py

import jwt
import os
from dotenv import load_dotenv
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import UntypedToken
from users.models import User
from urllib.parse import parse_qs

load_dotenv()

@database_sync_to_async
def get_user_from_token(token):
    try:
        JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = decoded_token.get('user_id')
        if not user_id:
            raise jwt.InvalidTokenError('Token payload missing user_id.')

        user = User.objects.get(id=user_id)
        if user.deleted:
            raise User.DoesNotExist('User account is deactivated.')
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope['query_string'].decode())
        token = query_string.get('token', [None])[0]

        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
