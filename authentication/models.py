from django.db import models
import uuid
from users.models import User

# Create your models here.
class ResetPassCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_user_reset_pass_code = models.ForeignKey(User, on_delete=models.CASCADE)
    val_reset_pass_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reset_pass_code'