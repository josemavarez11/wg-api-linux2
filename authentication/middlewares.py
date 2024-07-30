import jwt
import os
from django.http import JsonResponse
from users.models import User
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

class JWTMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    @staticmethod
    def get_token_from_header(header):
        parts = header.split()
        if len(parts) == 2 and parts[0] == 'Bearer':
            return parts[1]
        raise jwt.InvalidTokenError('Authorization header must start with Bearer.')

    @staticmethod
    def decode_jwt_token(token):
        JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])

    @staticmethod
    def get_user_from_token(decoded_token):
        user_id = decoded_token.get('user_id')
        if not user_id:
            raise jwt.InvalidTokenError('Token payload missing user_id.')
        user = User.objects.get(id=user_id)
        
        # Check if user is marked as deleted
        if user.deleted:
            raise User.DoesNotExist('User account is deactivated.')
            
        return user

def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        authorization_header = request.META.get('HTTP_AUTHORIZATION')

        if authorization_header:
            try:
                token = JWTMiddleware.get_token_from_header(authorization_header)
                decoded_token = JWTMiddleware.decode_jwt_token(token)
                user = JWTMiddleware.get_user_from_token(decoded_token)

                request.custom_user = user

                return view_func(request, *args, **kwargs)
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token has expired.'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token.'}, status=401)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found or not active'}, status=404)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'No token provided.'}, status=401)

    return _wrapped_view

class AdminMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    @staticmethod
    def get_token_from_header(header):
        parts = header.split()
        if len(parts) == 2 and parts[0] == 'Bearer':
            return parts[1]
        raise jwt.InvalidTokenError('Authorization header must start with Bearer.')

    @staticmethod
    def decode_jwt_token(token):
        return jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])

    @staticmethod
    def get_user_from_token(decoded_token):
        user_id = decoded_token.get('user_id')
        if not user_id:
            raise jwt.InvalidTokenError('Token payload missing user_id.')
        return User.objects.get(id=user_id)

    @staticmethod
    def is_user_admin(user):
        return user.id_profile_user.des_profile == 'Admin'

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        authorization_header = request.META.get('HTTP_AUTHORIZATION')

        if authorization_header:
            try:
                token = AdminMiddleware.get_token_from_header(authorization_header)
                decoded_token = AdminMiddleware.decode_jwt_token(token)
                user = AdminMiddleware.get_user_from_token(decoded_token)

                if not AdminMiddleware.is_user_admin(user):
                    return JsonResponse({'error': 'Unauthorized'}, status=401)

                return view_func(request, *args, **kwargs)
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token has expired.'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token.'}, status=401)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'No token provided.'}, status=401)
    
    return _wrapped_view