from django.urls import path
from . import views

urlpatterns = [
    path('create-learning-phase/', views.create_learning_phase, name='create-learning-phase'),
    path('get-learning-phases/', views.get_learning_phases, name='get-learning-phases'),
    path('create-learning-step/', views.create_learning_step, name='create-learning-step'),
    path('get-learning-steps/', views.get_learning_steps, name='get-learning-steps'),
    path('create-deck/', views.create_deck, name='create-deck'),
    path('get-decks-by-user/', views.get_decks_by_user, name='get-decks-by-user'),
    path('get-cards-by-deck/<uuid:id_deck>/', views.get_cards_by_deck, name='get-cards-by-deck'),
    path('delete-deck/<uuid:id_deck>/', views.delete_deck, name='delete-deck'),
    path('update-deck/<uuid:id_deck>/', views.update_deck, name='update-deck'),
    path('reset-deck-progress/<uuid:id_deck>/', views.reset_deck_progress, name='reset-deck-progress'),
    path('create-card/', views.create_card, name='create-card'),
    path('generate-cards-with-ai/', views.generate_cards_with_ai, name='generate_cards_with_ai'),
    path('update-card/<uuid:id_card>/', views.update_card, name='update-card'),
    path('review-card/<uuid:id_card>/', views.review_card, name='review-card'),
    path('delete-card/<uuid:id_card>/', views.delete_card, name='delete-card'),
]
