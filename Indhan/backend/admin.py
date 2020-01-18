from django.contrib import admin
from .models import UserAccount, Mileage, Distance, FuelConsumed, CurrentData, PetrolPump

admin.site.register(UserAccount)
admin.site.register(Mileage)
admin.site.register(Distance)
admin.site.register(FuelConsumed)
admin.site.register(CurrentData)
admin.site.register(PetrolPump)

# Register your models here.
