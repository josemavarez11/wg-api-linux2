from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from authentication.middlewares import admin_required, jwt_required
from .serializers import DeckSerializer, CardSerializer, LearningPhaseSerializer, LearningStepSerializer
from .models import Deck, Card, LearningPhase, LearningStep
from .utils import register_new_card, parse_cards_string_to_dict, evaluate_card, get_cards_to_review
from ia.views import generate_study_cards
from learning.models import UserPreference

# Create your views here.

#@admin_required
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

#@admin_required
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
    id_user = request.custom_user.id
    data = request.data.copy()

    data['id_user'] = id_user
    serializer = DeckSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@jwt_required
@api_view(['GET'])
def get_decks_by_user(request):
    id_user = request.custom_user.id
    decks = Deck.objects.filter(id_user=id_user)
            
    serializer = DeckSerializer(decks, many=True)
            
    for deck in serializer.data:
        cards = Card.objects.filter(id_deck=deck['id'])
        deck['cards_amount'] = cards.count()
        
    return Response(serializer.data, status=status.HTTP_200_OK)

@jwt_required
@api_view(['GET'])
def get_cards_by_deck(request, id_deck):
    deck = get_object_or_404(Deck, id=id_deck)
    cards = Card.objects.filter(id_deck=deck)
    serializer = CardSerializer(cards, many=True)

    if serializer.data == []:
        return Response('No cards found', status=status.HTTP_204_NO_CONTENT)
    
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
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@jwt_required
@api_view(['GET'])
def reset_deck_progress(request, id_deck):
    deck = get_object_or_404(Deck, id=id_deck)
    cards = Card.objects.filter(id_deck=deck)
    for card in cards:
        card.id_last_learning_step = None
        card.id_learning_phase = None
        card.fir_review_card = None
        card.las_review_card = None
        card.lap_card = False
        card.las_interval_card = 0
        card.nex_interval_card = 0
        card.eas_factor_card = 250
        card.rev_card = 0
        card.save()
    return Response(status=status.HTTP_200_OK)

@jwt_required
@api_view(['POST'])
def create_card(request):
    id_deck = request.data.get('id_deck')
    val_card = request.data.get('val_card')
    mea_card = request.data.get('mea_card')

    if not id_deck or not val_card or not mea_card:
        return Response({'message': 'Missing data'}, status=status.HTTP_400_BAD_REQUEST)

    deck = get_object_or_404(Deck, id=id_deck)
    card = register_new_card(deck.id, val_card, mea_card)

    return Response(card, status=status.HTTP_201_CREATED)

@jwt_required
@api_view(['DELETE'])
def delete_card(request, id_card):
    card = get_object_or_404(Card, id=id_card)
    card.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@jwt_required
@api_view(['PUT'])
def update_card(request, id_card):
    card = get_object_or_404(Card, id=id_card)

    if not request.data:
        return Response({'message': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    data = request.data.copy()

    if 'id_deck' in data:
        data.pop('id_deck')

    updated_data = {key: value for key, value in data.items() if getattr(card, key) != value}

    if not updated_data:
        return Response({'message': 'The data provided matches with the current data.'}, status=status.HTTP_304_NOT_MODIFIED)
    
    serializer = CardSerializer(card, data=updated_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@jwt_required
@api_view(['POST'])
def generate_cards_with_ai(request):
    id_user = request.custom_user.id
    id_deck = request.data.get('id_deck')
    cards_amount = request.data.get('cards_amount')
    topic = request.data.get('topic')
    user_prompt = request.data.get('user_prompt')

    if not (id_deck and cards_amount) or not (topic or user_prompt):
        return Response({'message': 'Missing data'}, status=status.HTTP_400_BAD_REQUEST)
    
    existing_cards = Card.objects.filter(id_deck=id_deck).values('val_card', 'mea_card')
    existing_cards_dict = { card['val_card']: card['mea_card'] for card in list(existing_cards) }

    user_preferences = UserPreference.objects.filter(id_user=id_user).select_related(
        'id_native_language', 'id_language_to_study'
    )

    if not user_preferences:
        return Response({'message': 'User preferences not found'}, status=status.HTTP_404_NOT_FOUND)

    deck = get_object_or_404(Deck, id=id_deck)

    try:
        cards = generate_study_cards(
            user_preferences[0].id_native_language.des_language,
            user_preferences[0].id_language_to_study.des_language,
            topic,
            cards_amount,
            user_prompt,
            existing_cards_dict
        )
        
        cards_dict = parse_cards_string_to_dict(cards)

        new_cards_data = []
        for key, value in cards_dict.items():
            new_card = register_new_card(deck.id, key, value)
            new_cards_data.append(new_card)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(new_cards_data, status=status.HTTP_201_CREATED)

@jwt_required
@api_view(['PUT'])
def review_card(request, id_card):
    id_learning_step = request.data.get('id_learning_step')
    if not id_card or not id_learning_step:
        return Response({'message': 'Missing data'}, status=status.HTTP_400_BAD_REQUEST)
    
    card = get_object_or_404(Card, id=id_card)
    deck = get_object_or_404(Deck, id=card.id_deck.id)

    try:
        card_evaluated = evaluate_card(card, id_learning_step, deck.ste_value, deck.gra_interval, deck.gra_max_interval)
    except Exception as e:
        return Response({'message': f'Evaluation error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        card_evaluated.save()
        serialized_card = CardSerializer(card_evaluated)
    except Exception as e:
        return Response({'message': f'Saving error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serialized_card.data, status=status.HTTP_200_OK)

@jwt_required
@api_view(['GET'])
def get_all_data_by_deck(request, id_deck):
    deck = get_object_or_404(Deck, id=id_deck)
    cards = Card.objects.filter(id_deck=deck)

    deck_serializer = DeckSerializer(deck)
    cards_serializer = CardSerializer(cards, many=True)
    
    cards_not_studied = Card.objects.filter(id_deck=deck, rev_card=0)
    cards_to_review = get_cards_to_review(cards_serializer.data)

    cards_not_studied_serializer = CardSerializer(cards_not_studied, many=True)

    response_data = {
        'deck_details': {
            'id': deck_serializer.data['id'],
            'name': deck_serializer.data['nam_deck'],
            'cards_amount': cards_serializer.data.__len__(),
            'cards_not_studied': {
                'amount': cards_not_studied_serializer.data.__len__(),
                'cards': cards_not_studied_serializer.data,
            },
            'cards_to_review': {
                'amount': cards_to_review.__len__(),
                'cards': cards_to_review,
            },
        },
        'cards_details': cards_serializer.data,
    }
    
    return Response(response_data, status=status.HTTP_200_OK)