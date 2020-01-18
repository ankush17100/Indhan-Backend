from django.db import models
from datetime import datetime
from django.conf import settings

# Create your models here.
class UserAccount(models.Model):
    username = models.CharField(max_length=20, default='')
    password = models.CharField(max_length=20, default='')
    vehicleModel = models.CharField(max_length=20)
    token = models.IntegerField(primary_key=True)

    def __str__(self):
        return self.username

class Mileage(models.Model):
    user = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    date = models.DateField()
    mileage  = models.DecimalField(decimal_places=2,max_digits=10)
    def __str__(self):
        return self.user.username+" | "+str(self.date)

class Distance(models.Model):
    user = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    date = models.DateField()
    distance = models.DecimalField(decimal_places=2,max_digits=10)
    def __str__(self):
        return self.user.username+" | "+str(self.date)

class FuelConsumed(models.Model):
    user = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    date = models.DateField()
    fuel = models.DecimalField(decimal_places=2,max_digits=10)
    def __str__(self):
        return self.user.username+" | "+str(self.date)

class CurrentData(models.Model):
    user = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    lon = models.FloatField()
    lat = models.FloatField()
    totalDistance = models.FloatField()
    petrolLevel = models.FloatField()
    petrolConsumed = models.FloatField()
    date = models.DateField()
    def __str__(self):
        return self.user.username+" | "+str(self.totalDistance)+" | "+str(self.petrolConsumed)

class PetrolPump(models.Model):
    name = models.CharField(max_length=20)
    rating = models.FloatField()
    number = models.IntegerField()
    GRating = models.FloatField()
    def __str__(self):
        return self.name+" | "+str(self.rating)