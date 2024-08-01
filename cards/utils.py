from datetime import datetime
from .serializers import CardSerializer

def register_new_card(id_deck, val_card, mea_card):
    serializer = CardSerializer(data={
        'id_deck_id': id_deck,
        'val_card': val_card,
        'mea_card': mea_card,
        'day_added_card': datetime.now(),
    })

    if serializer.is_valid():
        serializer.save()
        return serializer.data