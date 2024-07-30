from django.db import models
from users.models import User
import uuid

class LearningStep(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    des_learning_step = models.CharField(max_length=150, unique=True, null=False)

    class Meta:
        db_table = 'learning_step'

class LearningPhase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    des_learning_phase = models.CharField(max_length=150, unique=True, null=False)

    class Meta:
        db_table = 'learning_phase'

class Deck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    nam_deck = models.CharField(max_length=256, null=False)
    new_cards_per_day = models.PositiveIntegerField(default=0)
    gra_interval = models.PositiveIntegerField(default=24)
    ste_value = models.PositiveIntegerField(default=10)
    gra_max_interval = models.PositiveIntegerField(default=180)

    class Meta:
        db_table = 'deck'

class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_deck = models.ForeignKey(Deck, null=False, on_delete=models.CASCADE)
    id_last_learning_step = models.ForeignKey(LearningStep, null=True, on_delete=models.CASCADE)
    id_learning_phase = models.ForeignKey(LearningPhase, null=True, on_delete=models.CASCADE)
    lap_card = models.BooleanField(default=False)
    las_interval_card = models.IntegerField(default=0)
    nex_interval_card = models.IntegerField(default=0)
    eas_factor_card = models.IntegerField(default=250)
    val_card = models.CharField(max_length=512, null=False)
    mea_card = models.CharField(max_length=512, null=False)
    day_added_card = models.DateTimeField(null=False)
    fir_review_card = models.DateTimeField(null=True)
    las_review_card = models.DateTimeField(null=True)
    rev_card = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'card'