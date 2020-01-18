from django.contrib import admin
from .models import UserAccount, Mileage, DistanceTravelled, FuelConsumed

admin.site.register(UserAccount)
admin.site.register(Mileage)
admin.site.register(DistanceTravelled)
admin.site.register(FuelConsumed)

# Register your models here.
