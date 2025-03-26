from django.db import models
from django.contrib.auth.models import User as user

# User Model
class User(models.Model):
   username = models.CharField(max_length=100)
   email = models.EmailField()
   password = models.CharField(max_length=100)
   
   def __str__(self):
      return self.username

# Occasion Model
class Occasion(models.Model):
   description = models.TextField()
   expender = models.CharField(max_length=200)
   utiliser = models.JSONField(default=list)
   created_by = models.ForeignKey(user, related_name='occasions', on_delete=models.CASCADE)
   
   def __str__(self):
      return self.description