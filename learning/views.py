from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from authentication.middlewares import admin_required, jwt_required
from .serializers import LanguageSerializer, LanguageLevelSerializer, ReasonToStudySerializer, TopicSerializer, UserPreferenceSerializer, UserPreferenceTopicSerializer
from .models import Language, LanguageLevel, ReasonToStudy, Topic, UserPreference, UserPreferenceTopic
from users.models import User

@api_view(['GET'])
def get_preference_options(request):
    languages = Language.objects.all()
    language_levels = LanguageLevel.objects.all()
    reasons_to_study = ReasonToStudy.objects.all()
    topics = Topic.objects.all()

    response_data = {
        "languages": LanguageSerializer(languages, many=True).data,
        "language_levels": LanguageLevelSerializer(language_levels, many=True).data,
        "reasons_to_study": ReasonToStudySerializer(reasons_to_study, many=True).data,
        "topics": TopicSerializer(topics, many=True).data
    }

    return Response(response_data, status=status.HTTP_200_OK)

@admin_required
@api_view(['POST'])
def create_topic(request):
    serializer = TopicSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def get_topics(request):
    topics = Topic.objects.all()
    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@admin_required
@api_view(['POST'])
def create_language(request):
    serializer = LanguageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_languages(request):
    languages = Language.objects.all()
    serializer = LanguageSerializer(languages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@admin_required
@api_view(['POST'])
def create_language_level(request):
    serializer = LanguageLevelSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_language_levels(request):
    language_levels = LanguageLevel.objects.all()
    serializer = LanguageLevelSerializer(language_levels, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@admin_required
@api_view(['POST'])
def create_reason_to_study(request):
    serializer = ReasonToStudySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_reasons_to_study(request):
    reasons_to_study = ReasonToStudy.objects.all()
    serializer = ReasonToStudySerializer(reasons_to_study, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@jwt_required
@api_view(['POST'])
def create_user_preference(request):
    user_id = request.custom_user.id
    
    data = request.data.copy()
    data['id_user'] = user_id
    serializer = UserPreferenceSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@admin_required
@api_view(['PUT'])
def update_user_preference(request, pk):
    user_preference = get_object_or_404(UserPreference, pk=pk)
    data = request.data.copy()

    updated_data = {key: value for key, value in data.items() if value is not None}

    if not updated_data:
        return Response(status=status.HTTP_400_BAD_REQUEST)
        
    serializer = UserPreferenceSerializer(user_preference, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.dat, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@admin_required 
@api_view(['DELETE'])
def delete_user_preference(request, pk):
    user_preference = get_object_or_404(UserPreference, pk=pk)
    user_preference.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@jwt_required
@api_view(['GET'])
def get_user_preference(request):
    user_id = request.custom_user.id
    user_preferences = UserPreference.objects.filter(id_user=user_id)

    if not user_preferences.exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserPreferenceSerializer(user_preferences, many=True)
    user_pref_data = serializer.data[0]

    native_language = get_object_or_404(Language, pk=user_pref_data['id_native_language'])
    language_to_study = get_object_or_404(Language, pk=user_pref_data['id_language_to_study'])
    language_to_study_level = get_object_or_404(LanguageLevel, pk=user_pref_data['id_language_to_study_level'])
    reason_to_study = get_object_or_404(ReasonToStudy, pk=user_pref_data['id_reason_to_study'])
    user_preference_topics = UserPreferenceTopic.objects.filter(id_user_preference=user_pref_data['id']).select_related('id_topic')

    topics = [
        {
            "id_topic": topic.id_topic_id,
            "description": topic.id_topic.des_topic
        }
        for topic in user_preference_topics
    ]
    
    response_data = {
        "id_user_preference": user_pref_data['id'],
        "user": {
            "id_user": request.user.id,
            "name": request.user.nam_user,
            "email": request.user.ema_user
        },
        "native_language": {
            "id_native_language": native_language.id,
            "description": native_language.des_language
        },
        "language_to_study": {
            "id_language_to_study": language_to_study.id,
            "description": language_to_study.des_language
        },
        "language_to_study_level": {
            "id_language_to_study_level": language_to_study_level.id,
            "description": language_to_study_level.des_language_level
        },
        "reason_to_study": {
            "id_reason_to_study": reason_to_study.id,
            "description": reason_to_study.des_reason_to_study
        },
        "topics": topics
    }

    return Response(response_data, status=status.HTTP_200_OK)

@jwt_required
@api_view(['POST'])
def create_user_preference_topic(request):
    serializer = UserPreferenceTopicSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@admin_required
@api_view(['PUT'])
def update_user_preference_topic(request, pk):
    user_preference_topic = get_object_or_404(UserPreferenceTopic, pk=pk)
    data = request.data.copy()

    updated_data = {key: value for key, value in data.items() if value is not None}

    if not updated_data:
        return Response({'error': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)
        
    serializer = UserPreferenceTopicSerializer(user_preference_topic, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@jwt_required
@api_view(['GET'])
def get_user_preference_topics(request):
    user_id = request.custom_user.id
    
    user_preference = get_object_or_404(UserPreference, id_user=user_id)
    user_preference_topics = UserPreferenceTopic.objects.filter(id_user_preference=user_preference.id)

    topics = [
        {
            "id_topic": topic.id_topic.id,
            "description": topic.id_topic.des_topic
        }
        for topic in user_preference_topics
    ]

    response_data = {
        "id_user": user_id,
        "id_user_preference": user_preference.id,
        "topics": topics
    }

    return Response(response_data, status=status.HTTP_200_OK)