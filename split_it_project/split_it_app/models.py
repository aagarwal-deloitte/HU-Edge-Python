from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User as user
from rest_framework.exceptions import ValidationError
from django.db.models import Sum

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
   
   def get_expenditure_summary(self):
      """ Generates the expenditure summary for the occasion. """
      
      events = self.event_occasions.all()
      
      summary = {
         'occasion': self.description,
         'total_expense': float(sum(event.amount for event in events)),
         'participants': self.participants,
         'total_no_of_events': len(events),
         'event_expense': {},
         'total_individual_expense': {},
         'cleared_expense': {},
         'total_active_expense': {},
      }
      
      for event in events:
         for user, amount in event.expense_split.items():
            summary['total_active_expense'][user] =  float(summary['total_active_expense'].get(user, 0.0) + amount)
      
      for event in events:
            summary['event_expense'][event.description] = event.amount
            
      cleared_expense = (
         ExpenditureSummary.objects.filter(event__in=events).values("user").annotate(total_cleared=Sum("amount")) # sums the cleared amount by user
      )
      
      for user, active_amount in summary['total_active_expense'].items():
         summary['total_individual_expense'][user] = active_amount
         
         
      for expense in cleared_expense:
         user = expense['user']
         cleared_amount = expense['total_cleared']
         summary['total_individual_expense'][user] = summary['total_individual_expense'].get(user, 0.0) + float(cleared_amount)
         
      for expense in cleared_expense:
         user = expense['user']
         cleared_amount = expense['total_cleared']
         summary['cleared_expense'][user] = float(cleared_amount)
            
      return summary
      
# Event Model
class Event(models.Model):
   description = models.TextField()
   amount = models.DecimalField(max_digits=20, decimal_places=2)
   expender = models.CharField(max_length=200)
   utiliser = models.JSONField(default=list)
   created_by = models.ForeignKey(user, related_name='events', on_delete=models.CASCADE)
   split_type = models.CharField(max_length=10, choices=[('equal', 'Equal'), ('unequal', 'Unequal')])
   occasion = models.ForeignKey(Occasion, related_name="event_occasions", on_delete=models.SET_NULL, null=True, blank=True)
   split = models.JSONField(default=list, null=True, blank=True)
   expense_split = models.JSONField(default=dict)
   
   class Meta:
      constraints = [
         models.UniqueConstraint(fields=['description', 'amount'], name='unique_event')
      ]
   
   def __str__(self):
      return self.description
   
   def calculate_split(self):
      """ Calculates the split based on the no of utilisers. """
      
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
      """ clears the expense of the user for the provided event. """
      
      if user in self.expense_split:
         if amount <= self.expense_split[user]:
            updated_expense_split = self.expense_split.copy()
            updated_expense_split[user] = updated_expense_split[user] - float(amount)
            self.expense_split = updated_expense_split
            super(Event, self).save(update_fields=['expense_split'])
            
            # adding log that this expense is cleared.
            ExpenditureSummary.objects.create(event=self, user=user, amount=amount)
            
            return True
         elif Decimal(str(self.expense_split[user])) == Decimal("0.00"):
            raise ValidationError({'message': f'Expense for this event is already cleared.'})
         else:
            raise ValidationError({'message': f'Amount provided is greater than expense split for user: {user}'})
      return False   
   
class ExpenditureSummary(models.Model):
   event = models.ForeignKey(Event, related_name='expenditure_history', on_delete=models.CASCADE)
   user = models.CharField(max_length=255)
   amount = models.DecimalField(max_digits=20, decimal_places=2)