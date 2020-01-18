from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
# Create your views here.
from .models import UserAccount, Mileage, Distance, FuelConsumed
import random
# Create your views here.

def login(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username,password)
        user = UserAccount.objects.get(username=username)
        if user.password==password:
            # Succesful login done
            print(user)
            # return Success and token
            returnObject = {
                'success':True,
                'token':user.token
            }
            return JsonResponse(returnObject)
        else:
            # Some problem with login
            print(user)  
            return JsonResponse({
                'success':False,
            })

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        vehicleModel = request.POST['model']
        token = [random.randint(1, 9) for a in range(0, 10)]
        token = "".join(str(x) for x in token)
        try:
            newuser = UserAccount.objects.get(username=username)
            if newuser:
                return JsonResponse({
                    'success':False,
                    'message':"This user already exits"
                })
        except:
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
        days = int(request.POST['days'])
        userAccount = UserAccount.objects.get(token=token)
        print(userAccount)
        if userAccount:
            mileage = Mileage.objects.filter(user = userAccount)
            # print(mileage)
            distance = Distance.objects.filter(user = userAccount)
            fuelConsumed = FuelConsumed.objects.filter(user = userAccount)
            # mileage = list(mileage[:days])
            # distance = list(distance[:days])
            # fuelConsumed = list(fuelConsumed[:days])
            print(mileage)
            print(distance)
            print(fuelConsumed)
            mileage = [x.mileage for x in mileage]
            distance = [x.distance for x in distance]
            fuelConsumed = [x.fuel for x in fuelConsumed]
            
            resposeObject = {
                'success':True,
                'mileage':mileage,
                'distance':distance,
                'fuel':fuelConsumed
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

# def TravelSessions(request):
    # if request.method == "POST":
