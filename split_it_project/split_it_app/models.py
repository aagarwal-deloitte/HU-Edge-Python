from django.db import models
# User Model
class User(models.Model):
   username = models.CharField(max_length=100)
   email = models.EmailField()
   password = models.CharField(max_length=100)
   
   def __str__(self):
      return self.username