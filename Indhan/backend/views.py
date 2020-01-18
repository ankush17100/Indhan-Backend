from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model, logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
# Create your views here.
from .models import UserAccount, Mileage, DistanceTravelled, FuelConsumed

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


def index(request):
    