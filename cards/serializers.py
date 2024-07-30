from rest_framework import serializers
from .models import LearningPhase, LearningStep, Deck, Card

class LearningPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPhase
        fields = '__all__'

class LearningStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningStep
        fields = '__all__'

class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = '__all__'

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'
