from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Occasion, Event

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email') 
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style = {'input_type': 'password'})
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password')
        
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class OccasionSerializer(serializers.ModelSerializer):
    
    #created_by_user = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()
    
    class Meta:
        model = Occasion
        fields = ('id', 'description', 'participants', 'events')
        
    # def get_created_by_user(self, attrs):
    #     return attrs.created_by.username
    
    def get_events(self, obj):
        events = Event.objects.filter(occasion=obj)
        if events.exists():
            return EventSerializer(events, many=True).data
        return  {}
    
class EventSerializer(serializers.ModelSerializer):
    
    occasion = serializers.CharField(write_only=True, required=False)
    occasion_name = serializers.SerializerMethodField()
    split = serializers.JSONField(write_only=True, required=False)
    
    class Meta:
        model = Event
        fields = ('id', 'description', 'occasion', 'occasion_name', 'amount', 'expender', 'utiliser', 'split_type', 'expense_split', 'split')
    
    def get_occasion_name(self, attrs):
        return attrs.occasion.description if attrs.occasion else ""
        
    def create(self, validated_data):
        occasion_description = validated_data.pop('occasion', None)
        
        if occasion_description:
            try:
                occasion =  Occasion.objects.get(description=occasion_description)
                validated_data['occasion'] = occasion
            except Occasion.DoesNotExist:
                raise serializers.ValidationError("Provided Occasion does not exist.")
            
        return Event.objects.create(**validated_data)