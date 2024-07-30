from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from authentication.middlewares import admin_required, jwt_required
from .serializers import DeckSerializer, CardSerializer, LearningPhaseSerializer, LearningStepSerializer
from .models import Deck, Card, LearningPhase, LearningStep

# Create your views here.

@admin_required
@api_view(['POST'])
def create_learning_phase(request):
    serializer = LearningPhaseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_learning_phases(request):
    learning_phases = LearningPhase.objects.all()
    serializer = LearningPhaseSerializer(learning_phases, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@admin_required
@api_view(['POST'])
def create_learning_step(request):
    serializer = LearningStepSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_learning_steps(request):
    learning_steps = LearningStep.objects.all()
    serializer = LearningStepSerializer(learning_steps, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@jwt_required
@api_view(['POST'])
def create_deck(request):
    serializer = DeckSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@jwt_required
@api_view(['GET'])
def get_decks_by_user(request):
    decks = Deck.objects.filter(id_user=request.user)
    serializer = DeckSerializer(decks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@jwt_required
@api_view(['GET'])
def get_cards_by_deck(request, id_deck):
    deck = get_object_or_404(Deck, id=id_deck)
    cards = Card.objects.filter(id_deck=deck)
    serializer = CardSerializer(cards, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@jwt_required
@api_view(['DELETE'])
def delete_deck(request, id_deck):
    deck = get_object_or_404(Deck, id=id_deck)
    deck.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@jwt_required
@api_view(['PUT'])
def update_deck(request, id_deck):
    deck = get_object_or_404(Deck, id=id_deck)

    if not request.data:
        return Response({'message': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    data = request.data.copy()

    if 'id_user' in data:
        data.pop('id_user')

    updated_data = {key: value for key, value in data.items() if getattr(deck, key) != value}

    if not updated_data:
        return Response({'message': 'The data provided matches with the current data.'}, status=status.HTTP_304_NOT_MODIFIED)
        
    serializer = DeckSerializer(deck, data=updated_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@jwt_required
@api_view(['GET'])
def reset_deck_progress(request, id_deck):
    deck = get_object_or_404(Deck, id=id_deck)
    cards = Card.objects.filter(id_deck=deck)
    for card in cards:
        card.lap_card = False
        card.las_interval_card = 0
        card.nex_interval_card = 0
        card.eas_factor_card = 250
        card.rev_card = 0
        card.save()
    return Response(status=status.HTTP_200_OK)