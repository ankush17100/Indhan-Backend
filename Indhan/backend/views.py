from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
# Create your views here.
from .models import UserAccount, Mileage, Distance, FuelConsumed, CurrentData
import random
import datetime
# Create your views here.
from math import sin,cos, pi
def deg2rad(deg):
    return deg*pi/180

def rad2deg(rad):
    return rad*180/pi

def distance(lat1,lon1,lat2,lon2):
    lat2 = float(lat2)
    lon2 = float(lat2)
    if(lat1==lat2 and lon1==lon2):
        return 0
    else:
        theta = lon1-lon2
        dist = sin(deg2rad(lat1))*sin(deg2rad(lat2))+cos(deg2rad(lat1))*cos(deg2rad(theta))
        dist = rad2deg(dist)
        dist = dist*60*1.1515
        dist = dist * 1.609344
        return dist

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

def d2f(a):
    return float(a)

def Refresh(request):
    if request.method == "POST":
        lat = float(request.POST['lat'])
        lon = float(request.POST['lon'])
        print("lat",request.POST)
        print("lon",lon)
        # time = request.POST['time']
        petrolLeft = float(request.POST['petrol'])
        token = request.POST['token']
        user = UserAccount.objects.get(token=token)
        lastData = CurrentData.objects.get(user=user)
        
        lastData.lon = d2f(lastData.lon)
        lastData.lat = d2f(lastData.lat)
        lastData.totalDistance = d2f(lastData.totalDistance)
        lastData.petrolLevel = d2f(lastData.petrolLevel)
        lastData.petrolConsumed = d2f(lastData.petrolConsumed)

        date = datetime.datetime.now().date()
        print(lat,lon,petrolLeft)
        if lastData.lat==0 and lastData.lon==0:
            lastData.lan = lat
            lastData.lon = lon
            lastData.petrolLeft = petrolLeft
            lastData.date = date
            lastData.save()
            print(1)
        elif lastData.date==date:
            # Increasing the distance traveled
            currentDistance = distance(lat,lon,lastData.lat,lastData.lon)
            lastData.lon = lon
            lastData.lat = lat
            lastData.totalDistance += currentDistance
            # Increaseing the petrol cosomption
            petrolConsumed = lastData.petrolLevel - petrolLeft
            lastData.petrolConsumed += petrolConsumed
            lastData.petrolLevel = petrolLeft
            lastData.save()
            print(2)
        else:
            finalDistance = lastData.totalDistance
            finalFuelConsumed = lastData.petrolConsumed
            finalMileage = finalDistance/finalFuelConsumed
            date = lastData.date
            newDistance = Distance(
                user = user,
                date = date,
                distance = finalDistance
            )
            newDistance.save()
            newFuel = FuelConsumed(
                user = user,
                date = date,
                fuel = finalFuelConsumed
            )
            newFuel.save()
            newMileage = Mileage(
                user = user,
                data = data,
                mileage = finalMileage
            )
            newMileage.save()
        return JsonResponse({
            'success':True
        })
    else:
        return JsonRespose({
            'success':False
        })

def Trip_plan(request):
    # start location 
    # destination location 
    # token 
    # distance of trip 
    
    # get the current value of petrol, 
    # multiply it with mileage latest of car 
    # (mileage from current day or from previous day)

    
    pass