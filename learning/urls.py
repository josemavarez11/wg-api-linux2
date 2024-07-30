from django.urls import path
from . import views

urlpatterns = [
    path('get-preference-options/', views.get_preference_options, name='get-preference-options'),
    path('create-language/', views.create_language, name='create-language'),
    path('get-languages/', views.get_languages, name='get-languages'),
    path('create-language-level/', views.create_language_level, name='create-language-level'),
    path('get-language-levels/', views.get_language_levels, name='get-language-levels'),
    path('create-reason-to-study/', views.create_reason_to_study, name='create-reason-to-study'),
    path('get-reasons-to-study/', views.get_reasons_to_study, name='get-reasons-to-study'),
    path('create-topic/', views.create_topic, name='create-topic'),
    path('get-topics/', views.get_topics, name='get-topics'),
    path('create-user-preference/', views.create_user_preference, name='create-user-preference'),
    path('delete-user-preference/<uuid:pk>/', views.delete_user_preference, name='delete-user-preference'),
    path('update-user-preference/<uuid:pk>/', views.update_user_preference, name='update-user-preference'),
    path('get-user-preference/', views.get_user_preference, name='get-user-preference'),
    path('create-user-preference-topic/', views.create_user_preference_topic, name='create-user-preference-topic'),
    path('update-user-preference-topic/<uuid:pk>/', views.update_user_preference_topic, name='update-user-preference-topic'),
    path('get-user-preference-topics/', views.get_user_preference_topics, name='get-user-preference-topics'),
]
