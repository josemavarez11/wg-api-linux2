from rest_framework import serializers
from .models import ResetPassCode

class ResetPassTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetPassCode
        fields = '__all__'