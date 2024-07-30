from rest_framework import serializers
from .models import UserPreference, UserPreferenceTopic, Language, LanguageLevel, ReasonToStudy, Topic

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

class LanguageLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageLevel
        fields = '__all__'

class ReasonToStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReasonToStudy
        fields = '__all__'

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = '__all__'

class UserPreferenceTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferenceTopic
        fields = '__all__'