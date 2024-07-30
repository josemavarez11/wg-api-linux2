from django.db import models
import uuid

# Create your models here.
class Message(models.Model): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    con_message = models.CharField(max_length=1200)
    con_response = models.CharField(max_length=1200)

    class Meta: 
        db_table = 'message'