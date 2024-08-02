from datetime import datetime
from .serializers import CardSerializer
import json

def register_new_card(id_deck, val_card, mea_card):
    serializer = CardSerializer(data={
        'id_deck': id_deck,
        'val_card': val_card,
        'mea_card': mea_card,
        'day_added_card': datetime.now(),
    })

    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else: 
        return serializer.errors
    
def parse_cards_string_to_dict(cards_str):
    data = json.loads(cards_str)
    
    # Cambiar los valores del diccionario a formato con guiones bajos
    cards_dict = {key: value.replace(' ', '_') for key, value in data.items()}
    
    return cards_dict