from datetime import datetime, timezone, timedelta
from .serializers import CardSerializer
import json
from .models import LearningPhase, LearningStep
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

LEARNING_STEPS = {
    "again": "Again",
    "hard": "Hard",
    "good": "Good",
    "easy": "Easy"
}


def evaluate_card(card, learning_step_id, step, graduating_interval, max_interval_days):

    DEFAULT_STARTING_EASE = 2.5  # 250%
    DEFAULT_HARD_INTERVAL = 1.2
    DEFAULT_EASY_BONUS = 1.3
    MINIMUM_EASE = 1.3

    try: ## STEP1
        # Obtener el learning step y la fase de aprendizaje desde la base de datos
        learning_step = LearningStep.objects.get(id=learning_step_id).des_learning_step
        #learning_phase = None if card.id_learning_phase is None else LearningPhase.objects.get(id=card.id_learning_phase).des_learning_phase
        learning_phase = LearningPhase.objects.get(id=card.id_learning_phase).des_learning_phase
    except Exception as e:
        raise Exception(f"STEP1: {str(e)}")

    try: ## STEP2
        last_interval = card.las_interval_card
        ease_factor = card.eas_factor_card / 100  # convertir de porcentaje a multiplicador
    except Exception as e:
        raise Exception(f"STEP2: {str(e)}")

    try: ## STEP3
        # Calcular nuevo intervalo y ease
        if learning_phase is None:  # Learning Phase
            if learning_step == "Again":
                new_interval = 1 / 24  # 1 minuto
            elif learning_step == "Hard":
                new_interval = 1 / 24  # 1 minuto
            elif learning_step == "Good":
                new_interval = graduating_interval  # Pasa a GP
                new_phase_id = LearningPhase.objects.get(des_learning_phase="Graduated Phase").id
                card.id_learning_phase = new_phase_id
            elif learning_step == "Easy":
                new_interval = graduating_interval * DEFAULT_EASY_BONUS  # Bonus adicional
                new_phase_id = LearningPhase.objects.get(des_learning_phase="Graduated Phase").id
                card.id_learning_phase = new_phase_id
            # Implementar uso de "step" para determinar los intervalos en LP
            new_interval = max(new_interval, step / 1440)  # Asegura que el intervalo no sea menor que "step"
        else:  # Graduated Phase
            if learning_step == "Again":
                card.lap_card = True
                new_interval = 10 / 1440  # 10 minutos
                ease_factor -= 0.2
            elif learning_step == "Hard":
                new_interval = last_interval * DEFAULT_HARD_INTERVAL
                ease_factor -= 0.15
            elif learning_step == "Good":
                new_interval = last_interval * ease_factor
            elif learning_step == "Easy":
                new_interval = last_interval * ease_factor * DEFAULT_EASY_BONUS
                ease_factor += 0.15
    except Exception as e:
        raise Exception(f"STEP3: {str(e)}")
    
    try: ## STEP4
        # Limitar el ease a un mínimo de 1.3
        ease_factor = max(ease_factor, MINIMUM_EASE)
        # Asegurar que el nuevo intervalo no sobrepase el intervalo máximo
        new_interval = min(new_interval, max_interval_days)
    except Exception as e:
        raise Exception(f"STEP4: {str(e)}")
    
    try: ## STEP5
        # Actualizar los valores de la carta
        card.las_interval_card = new_interval
        card.nex_interval_card = new_interval
        card.eas_factor_card = int(ease_factor * 100)  # convertir de vuelta a porcentaje
        card.las_review_card = datetime.now(timezone.utc).isoformat()
        card.rev_card += 1
    except Exception as e:
        raise Exception(f"STEP5: {str(e)}")
    
    try: ## STEP6
        # Calcular tiempos de repaso para cada learning step posible
        review_times = {
            "again": 1 / 24 if learning_phase is None else 10 / 1440,
            "hard": 1 / 24 if learning_phase is None else last_interval * DEFAULT_HARD_INTERVAL,
            "good": graduating_interval if learning_phase is None else last_interval * ease_factor,
            "easy": graduating_interval * DEFAULT_EASY_BONUS if learning_phase is None else last_interval * ease_factor * DEFAULT_EASY_BONUS
        }
    except Exception as e:
        raise Exception(f"STEP6: {str(e)}")
    
    return card, review_times