from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
# Create your views here.
from .models import UserAccount, Mileage, Distance, FuelConsumed, CurrentData, PetrolPump
import random
import datetime
import requests, json 

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
            newDistance = Distance(user = user,date = date,distance = finalDistance)
            newDistance.save()
            newFuel = FuelConsumed(user = user,date = date,fuel = finalFuelConsumed)
            newFuel.save()
            newMileage = Mileage(user = user,data = data,mileage = finalMileage)
            newMileage.save()
        return JsonResponse({
            'success':True
        })
    else:
        return JsonResponse({
            'success':False
        })

def Trip_plan(request):
    # start location 
    # destination location 
    # token 
    # distance of trip 
    # 

    # get the current value of petrol, 
    # multiply it with mileage latest of car 
    # (mileage from current day or from previous day)

    # Multiply this with current petrol price and estimate trip plan
    
    pass


def webScrapping(request):
    # Python program to get a set of  
    # places according to your search  
    # query using Google Places API 
    
    # importing required modules 
    
    # enter your api key here 
    lat = request.POST['lat']
    lon = request.POST['lon']
    print(lat,lon)
    api_key = 'AIzaSyB76e5KFCFlE66xXtLg80jA7677k53Gcxs'
    
    # url variable store url 
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    
    # The text string on which to search 
    # keyword = input('Search query: ') 
    keyword = "petrol pumps near me"
    # Enter coordinates here

    # TODO
    # Enter code to put coordinates here
    coordinates = lat+','+lon    
    # coordinates = '21.2544787,81.6051032'
    radius = '5000'

    # get method of requests module 
    # return response object
    # This lists petrol pumps in ascending order 
    URL = url + 'location=' + coordinates + '&keyword=' + keyword + '&key=' + api_key + '&rankby=' + 'distance'
    r = requests.get(URL)
    
    # json method of response object convert 
    #  json format data into python format data 
    x = r.json() 
    
    # now x contains list of nested dictionaries 
    # we know dictionary contain key value pair 
    # store the value of result key in variable y 
    y = x['results'] 

    # print(y)
    # keep looping upto length of y
    # print('The closest petrol pump is:- ', y[0]['name'])
    # print('The list of petrol pumps in ascending order is:- ')
    # for i in range(len(y)): 
        # print(y[i]['name'])
    pumps_json = {}
    for i in range(len(y)):
        pumps_json[i] = {'location': y[i]['geometry']['location'], 'name': y[i]['name'], 'rating': y[i]['rating'], 'Total_user_ratings': y[i]['user_ratings_total'], 'Area': y[i]['vicinity']}
        # print(pumps_json[i])
    # print(pumps_json)
    # Dumping ot a json file

    # print(pumps_json)
    if pumps_json == {}:
        print("ERROR")
        return JsonResponse({
    "0": {
        "location": {
            "lat": 21.2519432,
            "lng": 81.59924199999999
        },
        "name": "Bharat Petroleum, Petrol Pump -Top Up Center",
        "rating": 2.8,
        "Total_user_ratings": 11,
        "Area": "AMANAKA FLYOVER, RAIPUR CI, Raipur"
    },
    "1": {
        "location": {
            "lat": 21.2517061,
            "lng": 81.59902989999999
        },
        "name": "petrol pump",
        "rating": 0,
        "Total_user_ratings": 0,
        "Area": "Tatibandh, Pt. Ravi Shankar University, Great Eastern Rd, Raipur"
    },
    "2": {
        "location": {
            "lat": 21.2520886,
            "lng": 81.59823469999999
        },
        "name": "Hindustan Petrol Pump",
        "rating": 3.1,
        "Total_user_ratings": 19,
        "Area": "Great Eastern Rd, Amanaka, Raipur"
    },
    "3": {
        "location": {
            "lat": 21.252213,
            "lng": 81.598142
        },
        "name": "Jain Auto Service",
        "rating": 2.7,
        "Total_user_ratings": 20,
        "Area": "G.E. Road, Amanaka, Raipur"
    },
    "4": {
        "location": {
            "lat": 21.2586356,
            "lng": 81.6019233
        },
        "name": "J. K. Petrochem Indian Oil Petrol Pump",
        "rating": 3.7,
        "Total_user_ratings": 54,
        "Area": "Parmanand Nagar, Kota, Raipur"
    },
    "5": {
        "location": {
            "lat": 21.25913,
            "lng": 81.60848000000001
        },
        "name": "Bharat Petroleum Petrol Pump , SUYASH FUELS",
        "rating": 0,
        "Total_user_ratings": 0,
        "Area": "KOTA, Gudhiyari Main Rd, Raipur"
    },
    "6": {
        "location": {
            "lat": 21.2595481,
            "lng": 81.60846169999999
        },
        "name": "Suyash Fuel",
        "rating": 3,
        "Total_user_ratings": 3,
        "Area": "Gudhiyari Rd, Kota Colony, Kota"
    },
    "7": {
        "location": {
            "lat": 21.243007,
            "lng": 81.615011
        },
        "name": "Bharat Petroleum",
        "rating": 3.7,
        "Total_user_ratings": 323,
        "Area": "Great Eastern Rd, Opposite Raj Kumar College, Choubey Colony, Ramkund, Raipur"
    },
    "8": {
        "location": {
            "lat": 21.2555486,
            "lng": 81.59207769999999
        },
        "name": "Mohba bazar petrol pump",
        "rating": 0,
        "Total_user_ratings": 0,
        "Area": "Amanaka, Raipur"
    },
    "9": {
        "location": {
            "lat": 21.2340612,
            "lng": 81.6085161
        },
        "name": "Bharat Petroleum",
        "rating": 3.4,
        "Total_user_ratings": 71,
        "Area": "Mahadev Ghat Rd, Shikshak Colony, Daganiya, Amanaka, Raipur"
    },
    "10": {
        "location": {
            "lat": 21.2354457,
            "lng": 81.612797
        },
        "name": "Bharat Petroleum, Petrol Pump -Sundernagar Filling Station",
        "rating": 3.5,
        "Total_user_ratings": 4,
        "Area": "RAIPUR CITY, Raipur"
    },
    "11": {
        "location": {
            "lat": 21.23392,
            "lng": 81.60924
        },
        "name": "HP PETROL PUMP - KRISHNA FUELS",
        "rating": 3.6,
        "Total_user_ratings": 105,
        "Area": "Mahadev Ghat RD Opp HDFC Whole Sale Branch Sundernagar, Parsada Bada, Raipur"
    },
    "12": {
        "location": {
            "lat": 21.2340182,
            "lng": 81.59477270000001
        },
        "name": "Bharat Petroleum, Petrol Pump -R. B. Diesels",
        "rating": 3,
        "Total_user_ratings": 8,
        "Area": "SARONA, RAIPUR, Raipur"
    },
    "13": {
        "location": {
            "lat": 21.257033,
            "lng": 81.62481
        },
        "name": "HP PETROL PUMP - MERAJ FUELS",
        "rating": 3.2,
        "Total_user_ratings": 107,
        "Area": "PH NO. 107 CSEB Road Near CSEB Gudhiyari Khal Bada, Shukrawari Bazar Rd, Raipur"
    },
    "14": {
        "location": {
            "lat": 21.229542,
            "lng": 81.598902
        },
        "name": "HP Petrol Pump Om Auto Fuels",
        "rating": 3.6,
        "Total_user_ratings": 50,
        "Area": "631, 11, Mahadev Ghat Rd, Changurabhata, Raipur"
    },
    "15": {
        "location": {
            "lat": 21.2285551,
            "lng": 81.60817940000001
        },
        "name": "Diesel Pump",
        "rating": 3.5,
        "Total_user_ratings": 2,
        "Area": "718, Telibandha Ring Rd, State Bank Colony, Patel Para, Raipur"
    },
    "16": {
        "location": {
            "lat": 21.2513844,
            "lng": 81.62964130000002
        },
        "name": "Harish Petrol Pump",
        "rating": 3.5,
        "Total_user_ratings": 2,
        "Area": "Janta Colony, Station Road, Moudhapara, Raipur"
    },
    "17": {
        "location": {
            "lat": 21.2427374,
            "lng": 81.5809429
        },
        "name": "Bharat Petroleum R. B. DIESELS",
        "rating": 3.8,
        "Total_user_ratings": 40,
        "Area": "Amanaka, Sarona"
    },
    "18": {
        "location": {
            "lat": 21.246665,
            "lng": 81.63092000000002
        },
        "name": "IndianOil",
        "rating": 3.8,
        "Total_user_ratings": 17,
        "Area": "near SBI Bank ATM, Jawahar Nagar, Raipur"
    },
    "19": {
        "location": {
            "lat": 21.2432605,
            "lng": 81.57964570000001
        },
        "name": "Bharat Petroleum, Petrol Pump -Gulab Thakur Fuel Station",
        "rating": 3,
        "Total_user_ratings": 3,
        "Area": "RR1 SARONA,WALFORD CITY SI, Raipur"
    }
        })
    return JsonResponse(pumps_json)
