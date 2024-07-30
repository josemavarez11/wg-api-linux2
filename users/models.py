from django.db import models
import uuid

# Create your models here.
class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    des_subscription = models.CharField(max_length=90)
    pri_subscription = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'subscription'

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    des_profile = models.CharField(max_length=100)

    class Meta:
        db_table = 'profile'

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_subscription_user = models.ForeignKey(Subscription, on_delete=models.CASCADE, default='b6f69838-82c8-454e-9937-9ab61d235400')
    id_profile_user = models.ForeignKey(Profile, on_delete=models.CASCADE, default='5eab56af-60f5-4290-af60-a0dda32ee1af')
    nam_user = models.CharField(max_length=300)
    ema_user = models.CharField(max_length=300, unique=True)
    pas_user = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    profile_img_url = models.CharField(default='https://w7.pngwing.com/pngs/81/570/png-transparent-profile-logo-computer-icons-user-user-blue-heroes-logo.png')

    class Meta:
        db_table = 'user'