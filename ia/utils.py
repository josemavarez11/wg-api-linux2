from .prompts import prompts

def build_user_presentation_msg(user_info):
    name = user_info['name']
    native_language = user_info['preferences'][0]['native_language']
    language_to_study = user_info['preferences'][0]['language_to_study']
    language_to_study_level = user_info['preferences'][0]['language_to_study_level']
    reason_to_study = user_info['preferences'][0]['reason_to_study']
    topics = user_info['preferences'][0]['topics']

    topics_str = ', '.join(topics)

    #cómo hago para manejar el cambio de idiomas? hago una función traductor quizás?
    msg_template = prompts['chat']['user']['english']

    message = (
        msg_template
        .replace('[name]', name)
        .replace('[native_language]', native_language)
        .replace('[language_to_study]', language_to_study)
        .replace('[language_to_study_level]', language_to_study_level)
        .replace('[reason_to_study]', reason_to_study)
        .replace('[topics]', topics_str)
    )

    return message

def build_cards_generation_msg(language_to_speak, language_to_learn, topic, user_prompt, elements):
    msg_template = prompts['cards']['user']['english']
    elements_str = str(elements)
    message = (
        msg_template
        .replace('x1', language_to_speak)
        .replace('x2', language_to_learn)
        .replace('x3', user_prompt if user_prompt else topic)
        .replace('x4', elements_str)
    )

    return message