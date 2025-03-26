from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Occasion

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email') 
        
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password')
        
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class OccasionSerializer(serializers.ModelSerializer):
    
    created_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Occasion
        fields = ('id', 'description', 'expender', 'utiliser', 'created_by_user')
        
    def get_created_by_user(self, attrs):
        return attrs.created_by.username