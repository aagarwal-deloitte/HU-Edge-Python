from django.db import models
from django.contrib.auth.models import User as user

# User Model
class User(models.Model):
   username = models.CharField(max_length=100)
   email = models.EmailField()
   
   def __str__(self):
      return self.username

# Occasion Model
class Occasion(models.Model):
   description = models.TextField(unique=True)
   participants = models.JSONField(default=list)
   created_by = models.ForeignKey(user, related_name='occasions', on_delete=models.CASCADE)
      
   def __str__(self):
      return self.description
      
# Event Model
class Event(models.Model):
   description = models.TextField(unique=True)
   amount = models.DecimalField(max_digits=20, decimal_places=2)
   expender = models.CharField(max_length=200)
   utiliser = models.JSONField(default=list)
   created_by = models.ForeignKey(user, related_name='events', on_delete=models.CASCADE)
   split_type = models.CharField(max_length=10, choices=[('equal', 'Equal'), ('unequal', 'Unequal')])
   occasion = models.ForeignKey(Occasion, related_name="event_occasions", on_delete=models.SET_NULL, null=True, blank=True)
   split = models.JSONField(default=list, null=True, blank=True)
   
   def __str__(self):
      return self.description
   
   def calculate_split(self):
      if self.split_type == 'equal':
         split_amount = round((self.amount/len(self.utiliser)), 2)
         
         return {
            "expense_split": [
               { participant: split_amount for participant in self.utiliser}
            ]
         }
      elif self.split_type == 'unequal':
         return {
            "expense_split": [
               { participant: round(split_amount, 2) for participant, split_amount in zip(self.utiliser, self.split)}
            ]
         }