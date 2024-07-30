from django.db import models
import uuid

# Create your models here.
class Language(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    abb_language = models.CharField(max_length=10, unique=True, null=True)
    des_language = models.CharField(max_length=90)

    class Meta:
        db_table = 'language'

class LanguageLevel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    des_language_level = models.CharField(max_length=90)

    class Meta:
        db_table = 'language_level'

class ReasonToStudy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    des_reason_to_study = models.CharField(max_length=150)

    class Meta:
        db_table = 'reason_to_study'

class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    des_topic = models.CharField(max_length=150)

    class Meta:
        db_table = 'topic'

class UserPreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    id_native_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='native_language_preferences')
    id_language_to_study = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='study_language_preferences')
    id_language_to_study_level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE)
    id_reason_to_study = models.ForeignKey(ReasonToStudy, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_preference'
        unique_together = ('id_user', 'id_native_language', 'id_language_to_study', 'id_language_to_study_level', 'id_reason_to_study')


class UserPreferenceTopic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_user_preference = models.ForeignKey(UserPreference, on_delete=models.CASCADE)
    id_topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_preference_topic'
        unique_together = ('id_user_preference', 'id_topic')