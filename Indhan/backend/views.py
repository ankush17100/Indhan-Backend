from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model, logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

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
            return returnObject
        else:
            # Some problem with login
            print(userAccount)  
            return {'success':False}

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        phoneNumber = request.POST

def index(request):
    