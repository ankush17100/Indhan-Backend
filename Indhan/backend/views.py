from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model, logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
# Create your views here.
from .models import UserAccount, Mileage, Distance, FuelConsumed

# Create your views here.

def login(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        userAccount = UserAccount.objects.get(username = username,password=password)

        if userAccount is not None:
            # Succesful login done
            print(user)
            # return Success and token
            returnObject = {
                'success':True,
                'token':userAccount.token
            }
            return JsonResponse(returnObject)
        else:
            # Some problem with login
            print(userAccount)  
            return JsonResponse({
                'success':False}
                )

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        vehicleModel = request.POST['model']
        token = [random.randint(1, 9) for a in range(0, 10)]
        token = "".join(str(x) for x in token)
        userAccount = UserAccount(
            username = username,
            password = password,
            vehicleModel = vehicleModel,
            token = token
        )
        userAccount.save()
        return JsonResponse({
            'success':True,
            'token':token
        })


def home_screen(request):
    if request.method == "POST":
        token = request.POST['token']
        days = request.POST['days']
        userAccount = UserAccount.objects.get(token=token)
        if userAccount:
            mileage = Mileage.objects.filter(userAccount = userAccount).filter('date')
            distanceTravelled = DistanceTravelled.objects.filter(userAccount = userAccount).filter('date')
            fuelConsumed = FuelConsumed.objects.filter(userAccount = userAccount).filter('date')
            print(mileage)
            print(distanceTravelled)
            print(fuelConsumed)
            resposeObject = {
                'success':True,
                'mileage':mileage[:days],
                'distance':distanceTravelled[:days],
                'fuel':fuelConsumed[:days]
            }
            return JsonResponse(resposeObject)
        else:
            return JsonResponse({
                'success':False
            })

def DataEntry(request):
    if request.method == "POST":
        token = request.POST['token']
        date = request.POST['date']
        mileage = request.POST['mileage']
        distance = request.POST['distance']
        fuel = request.POST['fuel']
        userAccount = UserAccount.objects.get(token=token)
        if userAccount:
            newMilage = Mileage(
                user = userAccount,
                date = date,
                mileage = mileage
            )
            newMilage.save()
            newDistance = DistanceTravelled(
                user = userAccount,
                date = date,
                distance = distance
            )
            newDistance.save()
            newFuel = FuelConsumed(
                user = userAccount,
                date = date,
                fuel = fuel
            )
            newFuel.save()
            resposeObject = {
                'success':True,
            }
            return JsonResponse(resposeObject)

    else:
        pass
