from django.contrib import admin
from .models import UserAccount, Mileage, Distance, FuelConsumed

admin.site.register(UserAccount)
admin.site.register(Mileage)
admin.site.register(Distance)
admin.site.register(FuelConsumed)

# Register your models here.
