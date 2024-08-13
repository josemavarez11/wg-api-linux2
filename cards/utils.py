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

def evaluate_card(card, learning_step_id, step, graduating_interval, max_interval_days):
    DEFAULT_STARTING_EASE = 2.5  # 250%
    DEFAULT_HARD_INTERVAL = 0.8  # 80% del valor del step
    DEFAULT_EASY_BONUS = 1.3
    MINIMUM_EASE = 1.3

    try:  # STEP1
        # Obtener el learning step desde la base de datos
        learning_step_instance = LearningStep.objects.get(id=learning_step_id)
        learning_step = learning_step_instance.des_learning_step
        
        # Obtener la fase de aprendizaje actual
        if card.id_learning_phase:
            learning_phase = card.id_learning_phase.des_learning_phase  # Usa directamente la instancia
        else:
            learning_phase = None
    except Exception as e:
        raise Exception(f"STEP1: {str(e)}")

    try:  # STEP2
        last_interval = card.las_interval_card or 0
        ease_factor = card.eas_factor_card / 100  # convertir de porcentaje a multiplicador

        if card.fir_review_card is None:
            card.fir_review_card = datetime.now(timezone.utc).isoformat()  # Establecer la primera revisión
    except Exception as e:
        raise Exception(f"STEP2: {str(e)}")

    try:  # STEP3
        # Calcular nuevo intervalo y ease basado en la fase de aprendizaje
        if learning_phase is None:  # Learning Phase
            if learning_step == "Again":
                new_interval = 1  # 1 minuto
                card.id_learning_phase = LearningPhase.objects.get(des_learning_phase="Learning Phase")
            elif learning_step == "Hard":
                new_interval = max(step * DEFAULT_HARD_INTERVAL, 1)  # 80% del step
                card.id_learning_phase = LearningPhase.objects.get(des_learning_phase="Learning Phase")
            elif learning_step == "Good":
                new_interval = graduating_interval * 60  # Graduating Interval en minutos
                card.id_learning_phase = LearningPhase.objects.get(des_learning_phase="Graduated Phase")
            elif learning_step == "Easy":
                new_interval = graduating_interval * DEFAULT_EASY_BONUS * 60  # Bonus adicional en minutos
                card.id_learning_phase = LearningPhase.objects.get(des_learning_phase="Graduated Phase")
        else:  # Graduated Phase
            if learning_step == "Again":
                card.lap_card = True
                new_interval = 10  # 10 minutos
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

    try:  # STEP4
        # Limitar el ease a un mínimo de 1.3
        ease_factor = max(ease_factor, MINIMUM_EASE)
        # Asegurar que el nuevo intervalo no sobrepase el intervalo máximo
        new_interval = min(new_interval, max_interval_days * 1440)  # Convertir días a minutos
    except Exception as e:
        raise Exception(f"STEP4: {str(e)}")

    try:  # STEP5
        # Actualizar los valores de la carta
        card.las_interval_card = new_interval
        card.nex_interval_card = new_interval
        card.eas_factor_card = int(ease_factor * 100)  # convertir de vuelta a porcentaje
        card.las_review_card = datetime.now(timezone.utc).isoformat()
        card.rev_card += 1
        card.id_last_learning_step = learning_step_instance  # Asignar la instancia de LearningStep
    except Exception as e:
        raise Exception(f"STEP5: {str(e)}")

    try:  # STEP6
        # Calcular tiempos de repaso para cada learning step posible (en minutos)
        review_times = {
            "again": 1 if learning_phase is None else 10,
            "hard": max(step * DEFAULT_HARD_INTERVAL, 1) if learning_phase is None else round(last_interval * DEFAULT_HARD_INTERVAL),
            "good": round(graduating_interval * 60) if learning_phase is None else round(last_interval * ease_factor),
            "easy": round(graduating_interval * DEFAULT_EASY_BONUS * 60) if learning_phase is None else round(last_interval * ease_factor * DEFAULT_EASY_BONUS)
        }
    except Exception as e:
        raise Exception(f"STEP6: {str(e)}")

    return card, review_times