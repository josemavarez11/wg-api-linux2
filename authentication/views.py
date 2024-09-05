from datetime import timezone, datetime, timedelta
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.utils.crypto import get_random_string
from .models import ResetPassCode
from users.models import User
from dotenv import load_dotenv
import os
import jwt

load_dotenv()

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(ema_user=email, deleted=False)
    except User.DoesNotExist:
        return Response({'error': 'The data provided does not match the data in the database.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not check_password(password, user.pas_user):
        return Response({'error': 'The data provided does not match the data in the database.'}, status=status.HTTP_400_BAD_REQUEST)
    
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    token = jwt.encode({'user_id': str(user.id)}, JWT_SECRET_KEY, algorithm='HS256')

    user_data = {
        'id': user.id,
        'name': user.nam_user,
        'email': user.ema_user,
        'subscription': {
            'id': user.id_subscription_user.id,
            'description': user.id_subscription_user.des_subscription
        },
        'profile_img_url': user.profile_img_url
    }

    return Response({'user': user_data, 'token': token}, status=status.HTTP_200_OK)

@api_view(['POST'])
def send_reset_password_code(request):
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Please provide an email address'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(ema_user=email, deleted=False)
    except User.DoesNotExist:
        return Response({'error': 'No user associated with this email was found.'}, status=status.HTTP_400_BAD_REQUEST)
    
    reset_pass_code = get_random_string(length=6, allowed_chars='0123456789acdefjhijklnopqrtuvwxyz')
    ResetPassCode.objects.create(id_user_reset_pass_code=user, val_reset_pass_code=reset_pass_code)

    html_message = render_to_string('email.html', {'code': reset_pass_code})
    plain_message = strip_tags(html_message)

    message = EmailMultiAlternatives(
        subject = 'It looks like you have requested to reset your WiseGlot password.',
        body=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[email,]
    )

    message.attach_alternative(html_message, 'text/html')
    try:
        message.send()
    except Exception as e:
        return Response({'error': 'Failed to send email. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Reset password code sent successfully'}, status.HTTP_200_OK)

@api_view(['POST'])
def validate_reset_password_code(request):
    code = request.data.get('code')
    email = request.data.get('email')

    if not code or not email:
        return Response({'error': "Please provide both secret code and email"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        reset_pass_code = ResetPassCode.objects.get(val_reset_pass_code=code, id_user_reset_pass_code__ema_user=email)
    except ResetPassCode.DoesNotExist:
        return Response({'error': 'The code provided is invalid.'}, status=status.HTTP_400_BAD_REQUEST)
    
    current_time = datetime.now(timezone.utc)
    if (current_time - reset_pass_code.created_at) > timedelta(minutes=5):
        return Response({'error': 'The code provided has expired.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Validation successfully completed.'}, status.HTTP_200_OK)

@api_view(['POST'])
def reset_password(request):
    code = request.data.get('code')
    password = request.data.get('password')
    email = request.data.get('email')

    if not code or not email or not password:
        return Response({'error': 'Please provide all the required fields'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        ResetPassCode.objects.get(val_reset_pass_code=code)
    except ResetPassCode.DoesNotExist:
        return Response({'error': 'The code provided is invalid.'}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, ema_user=email, deleted=False)
    
    if check_password(password, user.pas_user):
        return Response({'error': 'The new password cannot be the same as the current password'}, status=status.HTTP_400_BAD_REQUEST)
    
    user.pas_user = make_password(password)
    user.save()

    return Response({'message': 'Password successfully reset'}, status.HTTP_200_OK)