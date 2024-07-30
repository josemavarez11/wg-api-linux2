from django.urls import path
from . import views

urlpatterns = [
    path('create-learning-phase/', views.create_learning_phase, name='create-learning-phase'),
    path('get-learning-phases/', views.get_learning_phases, name='get-learning-phases'),
    path('create-learning-step/', views.create_learning_step, name='create-learning-step'),
    path('get-learning-steps/', views.get_learning_steps, name='get-learning-steps'),
    path('create-deck/', views.create_deck, name='create-deck'),
    path('get-decks-by-user/', views.get_decks_by_user, name='get-decks-by-user'),
    path('get-cards-by-deck/<int:id_deck>/', views.get_cards_by_deck, name='get-cards-by-deck'),
    path('delete-deck/<int:id_deck>/', views.delete_deck, name='delete-deck'),
    path('update-deck/<int:id_deck>/', views.update_deck, name='update-deck'),
    path('reset-deck-progress/<int:id_deck>/', views.reset_deck_progress, name='reset-deck-progress'),
]