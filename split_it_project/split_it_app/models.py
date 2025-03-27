from django.db import models
from django.contrib.auth.models import User as user
from rest_framework.exceptions import ValidationError

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
   expense_split = models.JSONField(default=dict)
   
   def __str__(self):
      return self.description
   
   def calculate_split(self):
      if self.split_type == 'equal':
         split_amount = float(self.amount) /len(self.utiliser)
         return { participant: round(float(split_amount), 2) for participant in self.utiliser}
      
      elif self.split_type == 'unequal':
         return { participant: round(float(split_amount), 2) for participant, split_amount in zip(self.utiliser, self.split)}
      
   def save(self, *args, **kwargs):
      super(Event, self).save(*args, **kwargs)
      self.expense_split = self.calculate_split()
      super(Event, self).save(update_fields=['expense_split'])
      
   def clear_expense(self, user, amount):
      if user in self.expense_split:
         if amount <= self.expense_split[user]:
            updated_expense_split = self.expense_split.copy()
            updated_expense_split[user] = updated_expense_split[user] - float(amount)
            self.expense_split = updated_expense_split
            super(Event, self).save(update_fields=['expense_split'])
            return True
         else:
            raise ValidationError({'message': 'Amount provided is greater than expense split for user: {user}'})
      return False