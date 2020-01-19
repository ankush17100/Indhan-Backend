from django.urls import path
from django.conf.urls.static import static

from . import views

app_name = 'backend'

urlpatterns = [
    path('login',views.login,name='index'),
    path('signup',views.signup,name='signup'),
    path('index',views.home_screen,name="index"),
    path('data',views.DataEntry,name="data"),
    path('refresh',views.Refresh,name="refresh"),
    path('petrolpump',views.webScrapping,name="petrolpump"),
    path('cities_and_prices', views.cities_and_prices, name="cities_and_prices"),
    path('petrol_pump_ratings', views.petrol_pump_ratings, name="petrol_pump_ratings")
]