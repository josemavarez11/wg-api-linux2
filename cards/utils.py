from datetime import datetime, timezone
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

def evaluate_card(card, id_learning_step, graduating_interval, graduating_max_interval, step):

    graduating_max_interval = int(graduating_max_interval)  # Convert to integer
    now = datetime.now(timezone.utc)  # Actualizar el manejo de la fecha y hora
    
    # Convertir campos de fecha y hora a objetos datetime
    if card.fir_review_card:
        card.fir_review_card = datetime.fromisoformat(card.fir_review_card.replace('Z', '+00:00'))
    if card.las_review_card:
        card.las_review_card = datetime.fromisoformat(card.las_review_card.replace('Z', '+00:00'))
    
    try:
        # Comprobar si es la primera vez que se revisa la carta
        first_review = card.fir_review_card is None

        if not first_review:
            # Incrementar el contador de revisiones
            card.rev_card += 1

        if card.day_added_card:
            card.day_added_card = datetime.fromisoformat(card.day_added_card.replace('Z', '+00:00'))
    except Exception as e:
        raise Exception(f"Error al actualizar el contador de revisiones y la fecha de creación de la carta: {str(e)}")
    
    initial_ease = 2.50  # Factor de facilidad inicial predeterminado (como una fracción)

    def calculate_new_interval(minutes, factor):
        try:
            new_interval = max(1, round(minutes * factor))
            max_interval_minutes = graduating_max_interval * 24 * 60  # Transformar graduating_max_interval a minutos
            return min(new_interval, max_interval_minutes)  # Asegurar el límite máximo del intervalo
        except Exception as e:
            raise Exception(f"Error al calcular el nuevo intervalo: {str(e)}")
        
    def update_learning_phase(new_phase):
        try:
            new_phase_id = LearningPhase.objects.get(des_learning_phase=new_phase).id
            card.id_learning_phase = new_phase_id
        except Exception as e:
            raise Exception(f"Error al actualizar la fase de aprendizaje: {str(e)}")

    def within_bounds(e):
        try:
            return min(max(e, 1.3), 2.5)
        except Exception as e:
            raise Exception(f"Error al verificar los límites del factor de facilidad: {str(e)}")

    # Diccionario para contener el tiempo de revisión para cada paso de aprendizaje
    review_times = {
        "Again": None,
        "Hard": None,
        "Good": None,
        "Easy": None
    }

    # Lógica para la evaluación de la carta
    if first_review:
        try:
            # Primer revisión de la carta, Fase de Aprendizaje (LP)
            card.fir_review_card = now
            card.rev_card = 1

            learning_step = LearningStep.objects.get(id=id_learning_step).des_learning_step

            if learning_step == "Good":
                card.las_interval_card = step  # Intervalo en minutos
                card.nex_interval_card = step
                update_learning_phase('Graduated Phase')
            elif learning_step == "Hard":
                card.las_interval_card = 1  # 1 minuto
                card.nex_interval_card = 1
            elif learning_step == "Again":
                card.las_interval_card = 0
                card.nex_interval_card = 0
            elif learning_step == 'Easy':
                card.las_interval_card = step  # 10 minutos, transición inmediata a GP
                card.nex_interval_card = step
                card.eas_factor_card = initial_ease * 100

            card.las_review_card = now
        except Exception as e:
            raise Exception(f"Error al evaluar la carta en la primera revisión: {str(e)}")
    else:
        try:
            # Cartas en Fase de Aprendizaje (LP) o Graduadas (GP)
            learning_phase = LearningPhase.objects.get(id=card.id_learning_phase).des_learning_phase
            if learning_phase == 'Learning Phase':
                if learning_step == "Again":
                    card.lap_card = True
                    card.nex_interval_card = 10  # carta caducada, nuevo intervalo fijo a 10 minutos
                    card.eas_factor_card *= 0.8 
                elif learning_step == "Hard":
                    card.nex_interval_card = calculate_new_interval(card.las_interval_card, 1.2)
                    card.eas_factor_card *= 0.85
                elif learning_step == "Good":
                    card.nex_interval_card = calculate_new_interval(card.las_interval_card, 2.5)
                elif learning_step == "Easy":
                    card.nex_interval_card = calculate_new_interval(card.las_interval_card, 2.5 * 1.3)
                    card.eas_factor_card += 0.15

                card.eas_factor_card = within_bounds(card.eas_factor_card) * 100

            else:
                # Cuando la carta está en Fase de Aprendizaje (LP)
                if learning_step == "Hard":
                    card.nex_interval_card = 1  # aparece nuevamente en 1 minuto
                elif learning_step == "Good":
                    card.nex_interval_card = graduating_interval * 60  # transición a GP, convertir horas a minutos
                    update_learning_phase('Graduated Phase')
                elif learning_step == "Again":
                    card.nex_interval_card = 0
                elif learning_step == "Easy":
                    card.nex_interval_card = graduating_interval * 60  # transición a GP, convertir horas a minutos
                    card.eas_factor_card = (initial_ease - 0.20) * 100  # inicializando ease

                card.las_interval_card = card.nex_interval_card
        except Exception as e:
            raise Exception(f"Error al evaluar la carta en la revisión: {str(e)}")
        
        card.las_review_card = now

    try:
        # Actualizar el último paso de aprendizaje
        id_last_learning_step = LearningStep.objects.get(des_learning_step=learning_step).id
        card.id_last_learning_step = id_last_learning_step

        # Calcular tiempos de revisión para cada paso:
        if learning_phase == 'Graduated Phase':
            review_times["Again"] = 10
            review_times["Hard"] = calculate_new_interval(card.las_interval_card, 1.2)
            review_times["Good"] = calculate_new_interval(card.las_interval_card, 2.5)
            review_times["Easy"] = calculate_new_interval(card.las_interval_card, 2.5 * 1.3)
        else:
            # Learning Phase
            review_times["Again"] = 0
            review_times["Hard"] = 1
            review_times["Good"] = graduating_interval * 60  # Convertir horas a minutos
            review_times["Easy"] = graduating_interval * 60  # Convertir horas a minutos
    except Exception as e:
        raise Exception(f"Error al actualizar el último paso de aprendizaje y calcular los tiempos de revisión: {str(e)}")
    
    return card, review_times