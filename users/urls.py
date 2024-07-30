from django.urls import path
from . import views

urlpatterns = [
    path('create-profile/', views.create_profile, name='create-profile'),
    path('create-subscription/', views.create_subscription, name='create-subscription'),
    path('create-user/', views.create_user, name='create-user'),
    path('delete-user/', views.delete_user, name='delete-user'),
    path('update-user/', views.update_user, name='update-user'),
    path('get-user-data/', views.get_user_data, name='get-user-data'),
]