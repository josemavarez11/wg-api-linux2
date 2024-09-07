from datetime import datetime, timezone, timedelta
from .serializers import CardSerializer
import json
from .models import LearningPhase, LearningStep

def get_cards_to_review(cardsArray):
    cards_to_review = []
    current_time = datetime.now(timezone.utc)
    
    for card in cardsArray:
        if card['las_review_card'] is not None:
            last_review_time = datetime.fromisoformat(card['las_review_card'].replace('Z', '+00:00'))
            next_review_time = last_review_time + timedelta(minutes=card['nex_interval_card'])
            
            if next_review_time <= current_time:
                cards_to_review.append(card)
    
    return cards_to_review

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
    cards_dict = {key.replace('_', ' '): value.replace('_', ' ') for key, value in data.items()}
    
    return cards_dict

def evaluate_card(card, learning_step_id, step, graduating_interval, max_interval_days):
    DEFAULT_STARTING_EASE = 2.5  # 250%
    DEFAULT_HARD_INTERVAL = 0.8  # 80% del valor del step
    DEFAULT_EASY_BONUS = 1.3
    MINIMUM_EASE = 1.3
    MINIMUM_INTERVAL = 1  # 1 minuto mínimo


    print("<--------------------------------->")
    print("STARTING... Evaluating card")
    try:  # STEP1
        # Obtener el learning step desde la base de datos
        learning_step_instance = LearningStep.objects.get(id=learning_step_id)
        learning_step = learning_step_instance.des_learning_step
        print("STEP1. Learning step selected: ", learning_step)

        # Obtener la fase de aprendizaje actual
        if card.id_learning_phase:
            learning_phase = card.id_learning_phase.des_learning_phase
        else:
            learning_phase = None

        print("STEP1. Current card's learning phase: ", learning_phase)
    except Exception as e:
        raise Exception(f"STEP1: {str(e)}")

    try:  # STEP2
        last_interval = card.las_interval_card or MINIMUM_INTERVAL
        #current_interval = card.nex_interval_card or MINIMUM_INTERVAL
        current_interval = card.nex_interval_card
        ease_factor = card.eas_factor_card / 100  # Convertir de porcentaje a multiplicador
        print("STEP2. Card's latest interval found: ", current_interval)
        print("STEP2. Card's current ease factor: ", ease_factor)

        # Establecer la primera revisión si es la primera vez
        if card.fir_review_card is None:
            card.fir_review_card = datetime.now(timezone.utc).isoformat()
    except Exception as e:
        raise Exception(f"STEP2: {str(e)}")

    try:  # STEP3
        # Calcular el nuevo intervalo y ease basado en la fase de aprendizaje
        if learning_phase is None or learning_phase == "Learning Phase":  # Learning Phase
            print("STEP3. Evaluating the card as a Learning Phase card")
            if learning_step == "Again":
                print("STEP3. Evaluating the card as an 'Again' card")
                new_interval = MINIMUM_INTERVAL  # 1 minuto mínimo
                print("STEP3. New interval determined: ", new_interval)
                card.id_learning_phase = LearningPhase.objects.get(des_learning_phase="Learning Phase")
            elif learning_step == "Hard":
                print("STEP3. Evaluating the card as a 'Hard' card")
                #new_interval = max(step * DEFAULT_HARD_INTERVAL, MINIMUM_INTERVAL)  # 80% del step, asegurando un mínimo
                new_interval = step * DEFAULT_HARD_INTERVAL
                print("STEP3. New interval determined: ", new_interval)
                card.id_learning_phase = LearningPhase.objects.get(des_learning_phase="Learning Phase")
            elif learning_step == "Good" or learning_step == "Easy":
                print("STEP3. Evaluating the card as a 'Good' or 'Easy' card")
                new_interval = graduating_interval * 60  # Graduating Interval en minutos
                print("STEP3. New interval determined: ", new_interval)
                card.id_learning_phase = LearningPhase.objects.get(des_learning_phase="Graduated Phase")
        else:  # Graduated Phase
            print("STEP3. Evaluating the card as a Graduated Phase card")
            if learning_step == "Again":
                print("STEP3. Evaluating the card as an 'Again' card")
                card.lap_card = True
                new_interval = 10  # 10 minutos
                print("STEP3. New interval determined: ", new_interval)
                ease_factor -= 0.2
                print("STEP3. New ease factor determined: ", ease_factor)
                card.id_learning_phase = LearningPhase.objects.get(des_learning_phase="Learning Phase")
            elif learning_step == "Hard":
                print("STEP3. Evaluating the card as a 'Hard' card")
                #new_interval = max(last_interval * DEFAULT_HARD_INTERVAL, MINIMUM_INTERVAL)
                ease_factor -= 0.15
                new_interval = current_interval * 1.2
                print("STEP3. New interval determined: ", new_interval)
                print("STEP3. New ease factor determined: ", ease_factor)
            elif learning_step == "Good":
                print("STEP3. Evaluating the card as a 'Good' card")
                #new_interval = max(last_interval * ease_factor, MINIMUM_INTERVAL)
                new_interval = current_interval * ease_factor
                print("STEP3. New interval determined: ", new_interval)
            elif learning_step == "Easy":
                print("STEP3. Evaluating the card as an 'Easy' card")
                #new_interval = max(last_interval * ease_factor * DEFAULT_EASY_BONUS, MINIMUM_INTERVAL)
                new_interval = current_interval * ease_factor * DEFAULT_EASY_BONUS
                ease_factor += 0.15
                print("STEP3. New interval determined: ", new_interval)
                print("STEP3. New ease factor determined: ", ease_factor)

        # Limitar el ease a un mínimo de 1.3
        ease_factor = max(ease_factor, MINIMUM_EASE)
        print("STEP3. Final ease factor: ", ease_factor)

        # Asegurar que el nuevo intervalo no sobrepase el intervalo máximo
        new_interval = min(new_interval, max_interval_days * 1440)  # Convertir días a minutos
        print("STEP3. Final new interval: ", new_interval)

    except Exception as e:
        raise Exception(f"STEP3: {str(e)}")

    try:  # STEP4
        # Actualizar los valores de la carta
        card.nex_interval_card = new_interval
        if card.rev_card > 0:  # Solo actualizar si no es la primera vez
            print("STEP4. Not first card review")
            card.las_interval_card = current_interval
            card.las_review_card = datetime.now(timezone.utc).isoformat()
            card.id_last_learning_step = learning_step_instance
        else:
            print("STEP4. First card review")
            card.las_interval_card = None
            card.las_review_card = None
            card.id_last_learning_step = None
        card.eas_factor_card = int(ease_factor * 100)  # Convertir de vuelta a porcentaje
        card.rev_card += 1
    except Exception as e:
        raise Exception(f"STEP4: {str(e)}")

    print("DONE. Card evaluation completed.")
    print("<--------------------------------->")
    return card
