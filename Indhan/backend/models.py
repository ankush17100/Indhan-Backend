from django.db import models
from datetime import datetime
from django.conf import settings

# Create your models here.
class UserAccount(models.Model):
    username = models.CharField(max_length=20, default='1st')
    password = models.CharField(max_length=20)
    vehicleModel = models.CharField(max_length=20)
    token = models.IntegerField()
    def __str__(self):
        return self.username

class Mileage(models.Model):
    userAccount = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    date = models.DateField()
    mileage  = models.DecimalField(decimal_places=2,max_digits=10)

class DistanceTravelled(models.Model):
    userAccount = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    date = models.DateField()
    distance = models.DecimalField(decimal_places=2,max_digits=10)

class FuelConsumed(models.Model):
    userAccount = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    fuel = models.DecimalField(decimal_places=2,max_digits=10)
    date = models.DateField()


