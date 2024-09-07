from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from authentication.middlewares import jwt_required
from openai import OpenAI, OpenAIError, PermissionDeniedError
import os
from dotenv import load_dotenv
from .prompts import prompts
from .utils import build_user_presentation_msg, build_cards_generation_msg
from .models import Message
from .serializers import MessageSerializer
from users.views import get_user_preferences_data

load_dotenv()

@jwt_required
@api_view(['GET'])
def get_messages_by_user(request):
    id_user = request.custom_user.id
    
    messages = Message.objects.filter(id_user=id_user)
    serializer = MessageSerializer(messages, many=True)

    formatted_data = [
        {
            "con_message": message['con_message'],
            "con_response": message['con_response']
        }
        for message in serializer.data
    ]

    return Response(formatted_data, status.HTTP_200_OK)

def generate_study_cards(language_to_speak, language_to_learn, topic, elements, prompt, existing_cards):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        raise ConnectionError("Failed to initialize OpenAI client") from e
    
    try:
        user_msg = build_cards_generation_msg(language_to_speak, language_to_learn, topic, prompt, elements, existing_cards)
    except Exception as e:
        raise RuntimeError("Failed to build cards generation message", e) from e
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                { 
                    "role": "system",
                    "content": prompts['cards']['system']['english']
                },
                {"role": "user", "content": user_msg}
            ]
        )
    except PermissionDeniedError as e:
        return { "error": "Country, region, or territory not supported" }
    except OpenAIError as e:
        raise RuntimeError("OpenAI API request failed") from e
    except Exception as e:
        raise RuntimeError("An unexpected error occurred during the OpenAI API request", e) from e
    
    return response.choices[0].message.content

def create_msg_response(user_id, content_message):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        raise ConnectionError("Failed to initialize OpenAI client") from e

    user_info = get_user_preferences_data(user_id)
    if user_info is None:
        raise ValueError(f"No preferences found for user ID {user_id}")

    try:
        user_presentation_msg = build_user_presentation_msg(user_info)
        print('Presentation message:', user_presentation_msg)
    except Exception as e:
        raise RuntimeError("Failed to build user presentation message") from e

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                { 
                    "role": "system",
                    "content": prompts['chat']['system']['english']
                },
                {"role": "user", "content": user_presentation_msg},
                {"role": "user", "content": content_message}
            ],
            temperature=1.2,
            max_tokens=1500
        )
    except PermissionDeniedError as e:
        return { "error": "Country, region, or territory not supported" }
    except OpenAIError as e:
        raise RuntimeError("OpenAI API request failed") from e
    except Exception as e:
        raise RuntimeError("An unexpected error occurred during the OpenAI API request") from e

    return response.choices[0].message.content
