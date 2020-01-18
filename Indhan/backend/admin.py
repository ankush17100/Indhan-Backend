from django.contrib import admin
from .models import UserAccount, Mileage, Distance, FuelConsumed, CurrentData

admin.site.register(UserAccount)
admin.site.register(Mileage)
admin.site.register(Distance)
admin.site.register(FuelConsumed)
admin.site.register(CurrentData)

# Register your models here.
