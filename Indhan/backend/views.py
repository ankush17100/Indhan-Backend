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
import lxml
from bs4 import BeautifulSoup

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
		try:
			user = UserAccount.objects.get(username=username)
		except:
			return JsonResponse({'success': False, 'message': 'invalid username'})
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
			newData = CurrentData(
				user = userAccount,
				lon = 0.0,
				lat = 0.0,
				totalDistance = 0.0,
				petrolConsumed = 0.0,
				petrolLevel = 0.0,
				date = datetime.datetime.now().date()
			)
			newData.save()
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
		lastData = None
		try:
			lastData = CurrentData.objects.get(user=user)
		except:
			newData = CurrentData(
				user = user,
				lon = 0,
				lat = 0,
				totalDistance = 0,
				petrolConsumed = 0,
				petrolLevel = 0,
				date = datetime.datetime.now().date()
			)
			newData.save()
			lastData = newData
		lastData.lon = d2f(lastData.lon)
		lastData.lat = d2f(lastData.lat)
		lastData.totalDistance = d2f(lastData.totalDistance)
		lastData.petrolLevel = d2f(lastData.petrolLevel)
		lastData.petrolConsumed = d2f(lastData.petrolConsumed)
		print("===========REFRESH==========")
		date = datetime.datetime.now().date()
		print(lat,lon,petrolLeft)
		if lastData.lat==0 and lastData.lon==0:
			lastData.lan = lat
			lastData.lon = lon
			lastData.petrolLeft = petrolLeft
			lastData.date = date
			lastData.save()
			print("CASE 1")
		elif lastData.date==date:
			# Increasing the distance traveled
			currentDistance = distance(lat,lon,lastData.lat,lastData.lon)
			lastData.lon = lon
			lastData.lat = lat
			lastData.totalDistance += currentDistance
			# Increaseing the petrol cosomption
			if petrolLeft<lastData.petrolLevel:
				petrolConsumed = lastData.petrolLevel - petrolLeft
			else:
				petrolConsumed = 0
			lastData.petrolConsumed += petrolConsumed
			lastData.petrolLevel = petrolLeft
			lastData.save()
			print("CASE 2")
		else:
			finalDistance = lastData.totalDistance
			finalFuelConsumed = lastData.petrolConsumed
			finalMileage = finalDistance/finalFuelConsumed
			date = lastData.date
			newDistance = Distance(user = user,date = date,distance = finalDistance)
			newDistance.save()
			newFuel = FuelConsumed(user = user,date = date,fuel = finalFuelConsumed)
			newFuel.save()
			newMileage = Mileage(user = user,date = date,mileage = finalMileage)
			newMileage.save()
			print("CASE 3")
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
	current_price = 70
	# multiply it with mileage latest of car 
	# (mileage from current day or from previous day)

	user = UserAccount.objects.get(token=token)

	mileage = Mileage.objects.filter(user=user)


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
	print(lat, lon)
	if lat == "0.0":
		lat="21.2514"
		lon="81.6296"
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

def cities_and_prices(request):
	if request.method=="GET":
		r = requests.get('http://www.mypetrolprice.com/petrol-price-in-india.aspx')
		data = r.content

		soup = BeautifulSoup(data, 'lxml')
		mydivs = soup.findAll("div", {"class": "SF"})

		# print(mydivs[0])



		list1 = {}
		for a in range(0, len(mydivs)):
			t = mydivs[a]

			soup = BeautifulSoup(str(t ), 'lxml')

			place = soup.findAll("a")
			place = str(place[1])

			place = place[ : : -1]

			temp_place = ""
			# flag9 = 0
			
			place = place[4 : ]
			# print(place)
			for d in range(0, len(place)):
				# print( place[d])
				# if place[d]== ">" and place[d + 3] !="<":
					# flag9 = 1
				if place[d]== ">":

					# flag9= 0
					break
				# if flag9 == 1:
				temp_place += place[d]

			# print(temp_place)
			place = temp_place[ : : -1]
			# print(place)

			
			price = soup.findAll("b")
			list1[a] = {"place": place, "price": price[0].text}
		return JsonResponse(list1)

def petrol_pump_ratings(request):
	if request.method =="POST":
		lat = request.POST['lat']
		lon = request.POST['lon']

		if lat == "0.0":
			lat="21.2514"
			lon="81.6296"
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



		if y == []:
			y = [{'geometry': {'location': {'lat': 21.2513844, 'lng': 81.62964130000002}, 'viewport': {'northeast': {'lat': 21.25275162989272, 'lng': 81.63101507989272}, 'southwest': {'lat': 21.25005197010728, 'lng': 81.62831542010727}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'cef168c5a9f3d60afe694ff00352b6cffb321140', 'name': 'Harish Petrol Pump', 'place_id': 'ChIJn3Gjx5PdKDoRybXCCKIf28k', 'rating': 3.5, 'reference': 'ChIJn3Gjx5PdKDoRybXCCKIf28k', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 2, 'vicinity': 'Janta Colony, Station Road, Moudhapara, Raipur'}, {'geometry': {'location': {'lat': 21.2513844, 'lng': 81.62964130000002}, 'viewport': {'northeast': {'lat': 21.25275162989272, 'lng': 81.63101507989272}, 'southwest': {'lat': 21.25005197010728, 'lng': 81.62831542010727}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '7aec0dbbf40909626382bf1efd7277a45a564664', 'name': 'Civil Court', 'place_id': 'ChIJn3Gjx5PdKDoRsauNsBisI_I', 'rating': 4.5, 'reference': 'ChIJn3Gjx5PdKDoRsauNsBisI_I', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 2, 'vicinity': 'Janta Colony, Station Road, Moudhapara, Raipur'}, {'geometry': {'location': {'lat': 21.2513844, 'lng': 81.62964130000002}, 'viewport': {'northeast': {'lat': 21.25275162989272, 'lng': 81.63101507989272}, 'southwest': {'lat': 21.25005197010728, 'lng': 81.62831542010727}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/generic_business-71.png', 'id': 'e50504fbaef509056cf577d28c3391cff0dad76d', 'name': 'Shri Jagannath Petrol Pump', 'place_id': 'ChIJn3Gjx5PdKDoRss5Lf6oiz5g', 'rating': 0, 'reference': 'ChIJn3Gjx5PdKDoRss5Lf6oiz5g', 'scope': 'GOOGLE', 'types': ['point_of_interest', 'establishment'], 'user_ratings_total': 0, 'vicinity': '2, Shri Jagannath Mandir Parisar, Gayatri Nagar, Raipur'}, {'geometry': {'location': {'lat': 21.2551492, 'lng': 81.6303858}, 'viewport': {'northeast': {'lat': 21.25650452989272, 'lng': 81.63171642989273}, 'southwest': {'lat': 21.25380487010728, 'lng': 81.62901677010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '3edf8a731ab842a53a3bdd964488ac2c35e7f1d4', 'name': 'Popular Petrol Supply Co', 'place_id': 'ChIJFS6nB5LdKDoRhL6KhyYSxjs', 'rating': 4.5, 'reference': 'ChIJFS6nB5LdKDoRhL6KhyYSxjs', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 2, 'vicinity': 'Plot No:204, Station Road, Opp Hotel Panchsheel, Karveer'}, {'geometry': {'location': {'lat': 21.246665, 'lng': 81.63092000000002}, 'viewport': {'northeast': {'lat': 21.24802172989272, 'lng': 81.63222032989273}, 'southwest': {'lat': 21.24532207010728, 'lng': 81.62952067010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '23faeca6c51a94d4b2854eaf3a4acec939001914', 'name': 'IndianOil', 'opening_hours': {'open_now': False}, 'place_id': 'ChIJhQTZgZbdKDoRlPPfGIO6j-w', 'plus_code': {'compound_code': '6JWJ+M9 Raipur, Chhattisgarh', 'global_code': '7MH36JWJ+M9'}, 'rating': 3.8, 'reference': 'ChIJhQTZgZbdKDoRlPPfGIO6j-w', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 17, 'vicinity': 'near SBI Bank ATM, Jawahar Nagar, Raipur'}, {'geometry': {'location': {'lat': 21.247542, 'lng': 81.6352907}, 'viewport': {'northeast': {'lat': 21.24889197989273, 'lng': 81.63657737989271}, 'southwest': {'lat': 21.24619232010728, 'lng': 81.63387772010726}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'fd844a4db07d949a237d4cc3b562404bbddb1573', 'name': 'Bharat Petroleum, Petrol Pump -Ahmedji Bhai & Sons', 'opening_hours': {'open_now': True}, 'place_id': 'ChIJuzjvEKrdKDoR4uf9sZikGis', 'plus_code': {'compound_code': '6JXP+24 Raipur, Chhattisgarh', 'global_code': '7MH36JXP+24'}, 'rating': 3, 'reference': 'ChIJuzjvEKrdKDoR4uf9sZikGis', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 4, 'vicinity': 'JAISTAMBH CHOWK, RAIPUR CI, Raipur'}, {'geometry': {'location': {'lat': 21.257033, 'lng': 81.62481}, 'viewport': {'northeast': {'lat': 21.25842387989272, 'lng': 81.62623467989272}, 'southwest': {'lat': 21.25572422010728, 'lng': 81.62353502010727}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'eab5ab2d2e4201787cb04b19c06faa2fe34bdccf', 'name': 'HP PETROL PUMP - MERAJ FUELS', 'opening_hours': {'open_now': True}, 'place_id': 'ChIJuXyez_LdKDoR-srzwvl4PAg', 'plus_code': {'compound_code': '7J4F+RW Raipur, Chhattisgarh', 'global_code': '7MH37J4F+RW'}, 'rating': 3.2, 'reference': 'ChIJuXyez_LdKDoR-srzwvl4PAg', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 107, 'vicinity': 'PH NO. 107 CSEB Road Near CSEB Gudhiyari Khal Bada, Shukrawari Bazar Rd, Raipur'}, {'geometry': {'location': {'lat': 21.2565128, 'lng': 81.63569609999999}, 'viewport': {'northeast': {'lat': 21.25790622989273, 'lng': 81.63705172989272}, 'southwest': {'lat': 21.25520657010728, 'lng': 81.63435207010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'fc2d313df9228098a2f963bb3849db678b3c74d4', 'name': 'Daga Petrol Pump', 'opening_hours': {'open_now': True}, 'photos': [{'height': 4608, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/112827700284920291323">Ashish Sharma</a>'], 'photo_reference': 'CmRaAAAAco7yShOOBZImEgTvcC_tXdhvhXYp_SLP1n_imdv54_J1I04V3QivhzKbgsbKVOXRs3BxpORxDOdozZe6IK14mHVI1GrblCCJzOawKWSzqEgojkumh1kNqfC87wKhfujuEhBnDa5d-S0uy7NmEpc8152eGhQn3ki9UYjmAeuDNOslxoWLyFrE9A', 'width': 3456}], 'place_id': 'ChIJ-ajU74_dKDoR4QjnwA9DUTs', 'plus_code': {'compound_code': '7J4P+J7 Raipur, Chhattisgarh', 'global_code': '7MH37J4P+J7'}, 'rating': 3.8, 'reference': 'ChIJ-ajU74_dKDoR4QjnwA9DUTs', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 519, 'vicinity': 'Station Rd, Nahar Para, Station Road, Moudhapara, Raipur'}, {'geometry': {'location': {'lat': 21.256577, 'lng': 81.636494}, 'viewport': {'northeast': {'lat': 21.25789557989272, 'lng': 81.63783242989273}, 'southwest': {'lat': 21.25519592010728, 'lng': 81.63513277010729}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'fb9f87e11b3cb7fc8169e3500f9ec3c1cc8e3424', 'name': 'Bharat Petroleum, Petrol Pump -Daga Brothers', 'opening_hours': {'open_now': True}, 'place_id': 'ChIJybuzTc_dKDoRQ6o73qYpPyo', 'plus_code': {'compound_code': '7J4P+JH Fafadih, Raipur, Chhattisgarh', 'global_code': '7MH37J4P+JH'}, 'rating': 3.6, 'reference': 'ChIJybuzTc_dKDoRQ6o73qYpPyo', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 7, 'vicinity': 'Raipura Chowk Rd, Fafadih, Raipur'}, {'geometry': {'location': {'lat': 21.2456166, 'lng': 81.6362666}, 'viewport': {'northeast': {'lat': 21.24696637989272, 'lng': 81.63757162989272}, 'southwest': {'lat': 21.24426672010728, 'lng': 81.63487197010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '761659f0e7cd51139200dd14e5bc584b5fba8cdc', 'name': 'Quality Filling Station', 'place_id': 'ChIJ9bePiZfdKDoR6Cr5G0-NNuY', 'rating': 3, 'reference': 'ChIJ9bePiZfdKDoR6Cr5G0-NNuY', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 1, 'vicinity': 'House Of 265, Behind Gayatri Mandir, Samata Colony, Samata Colony, Raipur'}, {'geometry': {'location': {'lat': 21.243796, 'lng': 81.6363779}, 'viewport': {'northeast': {'lat': 21.24520442989272, 'lng': 81.63770307989272}, 'southwest': {'lat': 21.24250477010728, 'lng': 81.63500342010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'e0b76eed666f497cb0558cd4b438aaf1c78663ee', 'name': 'Bharat Petroleum', 'photos': [{'height': 1080, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/114688963882099614778">Ranjesh Kumar</a>'], 'photo_reference': 'CmRaAAAAuGev_8Uh17EhFDjMOTiB-JIzHHq2obpvKLwRdbdLH6TL6b-8gtKwJdF9lXH20IG5He3h2lz5WRuUoTGBOHNMgiFK5MUEtskcLVgX4PxMpeZzKTCKeSYRouZ5EoaLpK_vEhC_QpUkhzkeKD9RppkRwD34GhQHK_BA2renWVKaqjBtOVoFpmi1Qw', 'width': 1920}], 'place_id': 'ChIJP1z2_5fdKDoRYk8CSf8BqqI', 'plus_code': {'compound_code': '6JVP+GH Raipur, Chhattisgarh', 'global_code': '7MH36JVP+GH'}, 'rating': 3.8, 'reference': 'ChIJP1z2_5fdKDoRYk8CSf8BqqI', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 82, 'vicinity': 'Great Eastern Rd, Ganeshram Nagar, Raipur'}, {'geometry': {'location': {'lat': 21.2437574, 'lng': 81.6363519}, 'viewport': {'northeast': {'lat': 21.24517567989272, 'lng': 81.63766582989271}, 'southwest': {'lat': 21.24247602010728, 'lng': 81.63496617010726}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'd2f3c83d1ca35d71d85a43f48abad94d0d70e564', 'name': 'BP Petrol Bunk', 'place_id': 'ChIJ32T7_5fdKDoRC7N74rB533g', 'plus_code': {'compound_code': '6JVP+GG Raipur, Chhattisgarh', 'global_code': '7MH36JVP+GG'}, 'rating': 0, 'reference': 'ChIJ32T7_5fdKDoRC7N74rB533g', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 0, 'vicinity': 'Ganeshram Nagar, Byron Bazar, Raipur'}, {'geometry': {'location': {'lat': 21.2517542, 'lng': 81.6411974}, 'viewport': {'northeast': {'lat': 21.25306007989272, 'lng': 81.64245652989273}, 'southwest': {'lat': 21.25036042010728, 'lng': 81.63975687010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'ec8cc44b46031b00b252c0012b032b6fda0a95b8', 'name': 'Aastha Fuels', 'opening_hours': {'open_now': True}, 'photos': [{'height': 2592, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/117409221616875047576">Hoosain Narker</a>'], 'photo_reference': 'CmRaAAAA_0wwDFlUY5g0Eet-Nhap4IMhn4mZkKaP0GwHrFmrdO6vrrkZcWO5NG3ZcPd988mzNBdeAViTTo11xiSiNRlW4Y-4XIU9Ke-G7wjg7EXRYz2gQ5eM8o5qpt562Mj9s5etEhBDEY_hs1RyZDYcAqqj7KKaGhSKGku9Jq2dIh1yOiSTgv9n5xuOCw', 'width': 4608}], 'place_id': 'ChIJb0ABjpvdKDoRrbSmnCGNur4', 'plus_code': {'compound_code': '7J2R+PF Raipur, Chhattisgarh', 'global_code': '7MH37J2R+PF'}, 'rating': 3.7, 'reference': 'ChIJb0ABjpvdKDoRrbSmnCGNur4', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 19, 'vicinity': 'Devendra Nagar, Raipur'}, {'geometry': {'location': {'lat': 21.251753, 'lng': 81.6412631}, 'viewport': {'northeast': {'lat': 21.25304647989272, 'lng': 81.64249662989273}, 'southwest': {'lat': 21.25034682010727, 'lng': 81.63979697010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '91ed8adc083748d500d5e8bca1255cd0768703b7', 'name': 'HP PETROL PUMP', 'opening_hours': {'open_now': True}, 'photos': [{'height': 1341, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/108784518866737615628">Muskan Parihar</a>'], 'photo_reference': 'CmRaAAAAwgo-jIni2yD-UawYephUjQpCdgRSmEbb-nGdCpLufb2OoCbkApYb7195YOqnmZ2yMu20uy7DFjvwG6RvJ2HpS1W00TDMtlLSFNFBVGwl1yBdQEfOsGLH9JB8W7tTcIUfEhAeQXmD5K-pqwWdYMQedv9KGhR55taSYC2e3Os9djrNYkH0VGpkLw', 'width': 1679}], 'place_id': 'ChIJL6dwjpvdKDoRQk1hTWwcebg', 'plus_code': {'compound_code': '7J2R+PG Devendra Nagar, Raipur, Chhattisgarh', 'global_code': '7MH37J2R+PG'}, 'rating': 3.3, 'reference': 'ChIJL6dwjpvdKDoRQk1hTWwcebg', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 32, 'vicinity': 'Jail Rd, Devendra Nagar, Raipur'}, {'geometry': {'location': {'lat': 21.24576, 'lng': 81.64059}, 'viewport': {'northeast': {'lat': 21.24715012989272, 'lng': 81.64205207989272}, 'southwest': {'lat': 21.24445047010728, 'lng': 81.63935242010727}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '7925659125dcc5687058ec5d7aef3f7a015f05bf', 'name': 'HP PETROL PUMP - ANOOP AUTO SERVICES', 'opening_hours': {'open_now': True}, 'photos': [{'height': 1840, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/115847946694899531286">hari puri</a>'], 'photo_reference': 'CmRaAAAAsjf7Qh262vQwL8P-nIqOTVcq1mJLC9y8V7gHW69A1GZotcr586arpgIjkzDz-ZdiXyxEihT8OVdNDPEStXWAkpyoD4ERFhsE-oY3m8vyQKhrEa55-yJwlYUrus7rGE3SEhB4vx3oix_zmpvu_lX8dIcMGhRMhZeJVKZBNvD_xg8xncI1IWyFBQ', 'width': 3280}], 'place_id': 'ChIJS_CMwZjdKDoRgTeUShOpmuQ', 'plus_code': {'compound_code': '6JWR+86 Raipur, Chhattisgarh', 'global_code': '7MH36JWR+86'}, 'rating': 3.5, 'reference': 'ChIJS_CMwZjdKDoRgTeUShOpmuQ', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 13, 'vicinity': 'HPC Dealer G.E. Road, OPP Secretariate Post & Dist. (CG), Raipur'}, {'geometry': {'location': {'lat': 21.245662, 'lng': 81.640689}, 'viewport': {'northeast': {'lat': 21.24693847989272, 'lng': 81.64204587989272}, 'southwest': {'lat': 21.24423882010727, 'lng': 81.63934622010729}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'f552ce674afe3f5eaca047fa6eae9b73bef0996e', 'name': 'Club HP', 'place_id': 'ChIJfSeay5jdKDoRc-DULUASr2o', 'plus_code': {'compound_code': '6JWR+77 Raipur, Chhattisgarh', 'global_code': '7MH36JWR+77'}, 'rating': 2.8, 'reference': 'ChIJfSeay5jdKDoRc-DULUASr2o', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 4, 'vicinity': 'Mantalay Shashtri Chowk, Raipur'}, {'geometry': {'location': {'lat': 21.2396833, 'lng': 81.62713330000001}, 'viewport': {'northeast': {'lat': 21.24092867989272, 'lng': 81.62845082989271}, 'southwest': {'lat': 21.23822902010728, 'lng': 81.62575117010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '3f13daec9c2fa8aadce255b626f38c52cc5007f1', 'name': 'Alterantive Fuel', 'place_id': 'ChIJAQ_fDb_dKDoRAw8Wwyb_n2w', 'rating': 5, 'reference': 'ChIJAQ_fDb_dKDoRAw8Wwyb_n2w', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 1, 'vicinity': '16/512, Azad Chowk, G E Road, Azad Chowk, Raipur'}, {'geometry': {'location': {'lat': 21.2458224, 'lng': 81.6416426}, 'viewport': {'northeast': {'lat': 21.24717257989272, 'lng': 81.64302622989273}, 'southwest': {'lat': 21.24447292010727, 'lng': 81.64032657010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '0800bab8ff45d9b6a70001a42f1eff08e45001bf', 'name': 'Chawla Service station', 'opening_hours': {'open_now': True}, 'place_id': 'ChIJIdGIy5jdKDoR79MbwkjAWWg', 'plus_code': {'compound_code': '6JWR+8M Raipur, Chhattisgarh', 'global_code': '7MH36JWR+8M'}, 'rating': 3.3, 'reference': 'ChIJIdGIy5jdKDoR79MbwkjAWWg', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 3, 'vicinity': 'Jail Rd, Kutchery Chowk, Raipur, Moudhapara, Raipur'}, {'geometry': {'location': {'lat': 21.2456735, 'lng': 81.6416095}, 'viewport': {'northeast': {'lat': 21.24701732989272, 'lng': 81.64299942989273}, 'southwest': {'lat': 21.24431767010728, 'lng': 81.64029977010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '4294b74699a7d7e250f77c279e5b2ef636392e74', 'name': 'HP Petrol Pump - Chawla Service Station', 'opening_hours': {'open_now': True}, 'photos': [{'height': 4160, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/112890785733188340943">rameshwar kumar Sahu</a>'], 'photo_reference': 'CmRaAAAA6puWDFyOIVGlT5RKuhmmLXSv1VVXLv5Q1INNDCRFCrP_rCVzVjWgHjPLSYbYbVxynuwLDFq7tzkuapWVhTxzzMSlCF1M84h1CQHVSmlKRRZYR2NusDy1aD-M0LmnLnbNEhB_KmAcih_BpKcFqUWP8NBaGhSZKCntjvZOlj3gCGM6i-Z2Tk3RgQ', 'width': 3120}], 'place_id': 'ChIJKdT7y5jdKDoRoRvW1ul5kHw', 'plus_code': {'compound_code': '6JWR+7J Raipur, Chhattisgarh', 'global_code': '7MH36JWR+7J'}, 'rating': 3.7, 'reference': 'ChIJKdT7y5jdKDoRoRvW1ul5kHw', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 233, 'vicinity': 'OPP. Secretariate Shastri Chowk'}, {'geometry': {'location': {'lat': 21.243007, 'lng': 81.615011}, 'viewport': {'northeast': {'lat': 21.24425952989272, 'lng': 81.61632602989272}, 'southwest': {'lat': 21.24155987010728, 'lng': 81.61362637010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '860bb3929e99db9c5f8152d4aa2fff8a4184ec2a', 'name': 'Bharat Petroleum', 'opening_hours': {'open_now': True}, 'photos': [{'height': 3456, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/102773039998208852339">Archit7Ojha</a>'], 'photo_reference': 'CmRaAAAANMPfYG4v3XjfuVSA8_CYqHI5HByXMgrdGTnc52wE-ygCCx8oPRahDcUJENvAKeZKYsJCh7ANMIZnbpPVXMJMjLXTN0nVtLrWyQpBpUjoxlb2IBd6FFThQLZzs0CeRXW9EhDvodK47VU233QaXX8cXg7ZGhTck0HmvP_KDRoTn0sZrOg48sur_w', 'width': 4608}], 'place_id': 'ChIJYbJ7A-jdKDoRetdX40gmD1g', 'plus_code': {'compound_code': '6JV8+62 Raipur, Chhattisgarh', 'global_code': '7MH36JV8+62'}, 'rating': 3.7, 'reference': 'ChIJYbJ7A-jdKDoRetdX40gmD1g', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 323, 'vicinity': 'Great Eastern Rd, Opposite Raj Kumar College, Choubey Colony, Ramkund, Raipur'}]
		

		
		
		# keep looping upto length of y
		# print('The closest petrol pump is:- ', y[0]['name'])
		# print('The list of petrol pumps in ascending order is:- ')
		# for i in range(len(y)): 
			# print(y[i]['name'])
		petrol_pump = PetrolPump.objects.filter(name=y[0]["name"])
		if not petrol_pump:
			petrol_pump = PetrolPump(
				name=y[0]['name'],
				rating=0.0,
				number=0,
				GRating=y[0]['rating']
			)
			petrol_pump.save()
		else:
			petrol_pump = petrol_pump[0]
		print(petrol_pump)
		res   ={'location': y[0]['geometry']['location'], 'name': y[ 0]['name'], 'rating': y[0 ]['rating'], 'Total_user_ratings': y[0]['user_ratings_total'], 'Area': y[ 0]['vicinity'], 'app_ratings': petrol_pump.rating}
			# print(pumps_json[i])

		# Dumping ot a json file

		# print(pumps_json)

		
		return JsonResponse(res)

def petrol_pump_ratings_recommendation(request):
	if request.method =="POST":
		lat = request.POST['lat']
		lon = request.POST['lon']

		if lat == "0.0":
			lat="21.2514"
			lon="81.6296"
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



		if y == []:
			y = [{'geometry': {'location': {'lat': 21.2513844, 'lng': 81.62964130000002}, 'viewport': {'northeast': {'lat': 21.25275162989272, 'lng': 81.63101507989272}, 'southwest': {'lat': 21.25005197010728, 'lng': 81.62831542010727}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'cef168c5a9f3d60afe694ff00352b6cffb321140', 'name': 'Harish Petrol Pump', 'place_id': 'ChIJn3Gjx5PdKDoRybXCCKIf28k', 'rating': 3.5, 'reference': 'ChIJn3Gjx5PdKDoRybXCCKIf28k', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 2, 'vicinity': 'Janta Colony, Station Road, Moudhapara, Raipur'}, {'geometry': {'location': {'lat': 21.2513844, 'lng': 81.62964130000002}, 'viewport': {'northeast': {'lat': 21.25275162989272, 'lng': 81.63101507989272}, 'southwest': {'lat': 21.25005197010728, 'lng': 81.62831542010727}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '7aec0dbbf40909626382bf1efd7277a45a564664', 'name': 'Civil Court', 'place_id': 'ChIJn3Gjx5PdKDoRsauNsBisI_I', 'rating': 4.5, 'reference': 'ChIJn3Gjx5PdKDoRsauNsBisI_I', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 2, 'vicinity': 'Janta Colony, Station Road, Moudhapara, Raipur'}, {'geometry': {'location': {'lat': 21.2513844, 'lng': 81.62964130000002}, 'viewport': {'northeast': {'lat': 21.25275162989272, 'lng': 81.63101507989272}, 'southwest': {'lat': 21.25005197010728, 'lng': 81.62831542010727}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/generic_business-71.png', 'id': 'e50504fbaef509056cf577d28c3391cff0dad76d', 'name': 'Shri Jagannath Petrol Pump', 'place_id': 'ChIJn3Gjx5PdKDoRss5Lf6oiz5g', 'rating': 0, 'reference': 'ChIJn3Gjx5PdKDoRss5Lf6oiz5g', 'scope': 'GOOGLE', 'types': ['point_of_interest', 'establishment'], 'user_ratings_total': 0, 'vicinity': '2, Shri Jagannath Mandir Parisar, Gayatri Nagar, Raipur'}, {'geometry': {'location': {'lat': 21.2551492, 'lng': 81.6303858}, 'viewport': {'northeast': {'lat': 21.25650452989272, 'lng': 81.63171642989273}, 'southwest': {'lat': 21.25380487010728, 'lng': 81.62901677010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '3edf8a731ab842a53a3bdd964488ac2c35e7f1d4', 'name': 'Popular Petrol Supply Co', 'place_id': 'ChIJFS6nB5LdKDoRhL6KhyYSxjs', 'rating': 4.5, 'reference': 'ChIJFS6nB5LdKDoRhL6KhyYSxjs', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 2, 'vicinity': 'Plot No:204, Station Road, Opp Hotel Panchsheel, Karveer'}, {'geometry': {'location': {'lat': 21.246665, 'lng': 81.63092000000002}, 'viewport': {'northeast': {'lat': 21.24802172989272, 'lng': 81.63222032989273}, 'southwest': {'lat': 21.24532207010728, 'lng': 81.62952067010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '23faeca6c51a94d4b2854eaf3a4acec939001914', 'name': 'IndianOil', 'opening_hours': {'open_now': False}, 'place_id': 'ChIJhQTZgZbdKDoRlPPfGIO6j-w', 'plus_code': {'compound_code': '6JWJ+M9 Raipur, Chhattisgarh', 'global_code': '7MH36JWJ+M9'}, 'rating': 3.8, 'reference': 'ChIJhQTZgZbdKDoRlPPfGIO6j-w', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 17, 'vicinity': 'near SBI Bank ATM, Jawahar Nagar, Raipur'}, {'geometry': {'location': {'lat': 21.247542, 'lng': 81.6352907}, 'viewport': {'northeast': {'lat': 21.24889197989273, 'lng': 81.63657737989271}, 'southwest': {'lat': 21.24619232010728, 'lng': 81.63387772010726}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'fd844a4db07d949a237d4cc3b562404bbddb1573', 'name': 'Bharat Petroleum, Petrol Pump -Ahmedji Bhai & Sons', 'opening_hours': {'open_now': True}, 'place_id': 'ChIJuzjvEKrdKDoR4uf9sZikGis', 'plus_code': {'compound_code': '6JXP+24 Raipur, Chhattisgarh', 'global_code': '7MH36JXP+24'}, 'rating': 3, 'reference': 'ChIJuzjvEKrdKDoR4uf9sZikGis', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 4, 'vicinity': 'JAISTAMBH CHOWK, RAIPUR CI, Raipur'}, {'geometry': {'location': {'lat': 21.257033, 'lng': 81.62481}, 'viewport': {'northeast': {'lat': 21.25842387989272, 'lng': 81.62623467989272}, 'southwest': {'lat': 21.25572422010728, 'lng': 81.62353502010727}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'eab5ab2d2e4201787cb04b19c06faa2fe34bdccf', 'name': 'HP PETROL PUMP - MERAJ FUELS', 'opening_hours': {'open_now': True}, 'place_id': 'ChIJuXyez_LdKDoR-srzwvl4PAg', 'plus_code': {'compound_code': '7J4F+RW Raipur, Chhattisgarh', 'global_code': '7MH37J4F+RW'}, 'rating': 3.2, 'reference': 'ChIJuXyez_LdKDoR-srzwvl4PAg', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 107, 'vicinity': 'PH NO. 107 CSEB Road Near CSEB Gudhiyari Khal Bada, Shukrawari Bazar Rd, Raipur'}, {'geometry': {'location': {'lat': 21.2565128, 'lng': 81.63569609999999}, 'viewport': {'northeast': {'lat': 21.25790622989273, 'lng': 81.63705172989272}, 'southwest': {'lat': 21.25520657010728, 'lng': 81.63435207010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'fc2d313df9228098a2f963bb3849db678b3c74d4', 'name': 'Daga Petrol Pump', 'opening_hours': {'open_now': True}, 'photos': [{'height': 4608, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/112827700284920291323">Ashish Sharma</a>'], 'photo_reference': 'CmRaAAAAco7yShOOBZImEgTvcC_tXdhvhXYp_SLP1n_imdv54_J1I04V3QivhzKbgsbKVOXRs3BxpORxDOdozZe6IK14mHVI1GrblCCJzOawKWSzqEgojkumh1kNqfC87wKhfujuEhBnDa5d-S0uy7NmEpc8152eGhQn3ki9UYjmAeuDNOslxoWLyFrE9A', 'width': 3456}], 'place_id': 'ChIJ-ajU74_dKDoR4QjnwA9DUTs', 'plus_code': {'compound_code': '7J4P+J7 Raipur, Chhattisgarh', 'global_code': '7MH37J4P+J7'}, 'rating': 3.8, 'reference': 'ChIJ-ajU74_dKDoR4QjnwA9DUTs', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 519, 'vicinity': 'Station Rd, Nahar Para, Station Road, Moudhapara, Raipur'}, {'geometry': {'location': {'lat': 21.256577, 'lng': 81.636494}, 'viewport': {'northeast': {'lat': 21.25789557989272, 'lng': 81.63783242989273}, 'southwest': {'lat': 21.25519592010728, 'lng': 81.63513277010729}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'fb9f87e11b3cb7fc8169e3500f9ec3c1cc8e3424', 'name': 'Bharat Petroleum, Petrol Pump -Daga Brothers', 'opening_hours': {'open_now': True}, 'place_id': 'ChIJybuzTc_dKDoRQ6o73qYpPyo', 'plus_code': {'compound_code': '7J4P+JH Fafadih, Raipur, Chhattisgarh', 'global_code': '7MH37J4P+JH'}, 'rating': 3.6, 'reference': 'ChIJybuzTc_dKDoRQ6o73qYpPyo', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 7, 'vicinity': 'Raipura Chowk Rd, Fafadih, Raipur'}, {'geometry': {'location': {'lat': 21.2456166, 'lng': 81.6362666}, 'viewport': {'northeast': {'lat': 21.24696637989272, 'lng': 81.63757162989272}, 'southwest': {'lat': 21.24426672010728, 'lng': 81.63487197010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '761659f0e7cd51139200dd14e5bc584b5fba8cdc', 'name': 'Quality Filling Station', 'place_id': 'ChIJ9bePiZfdKDoR6Cr5G0-NNuY', 'rating': 3, 'reference': 'ChIJ9bePiZfdKDoR6Cr5G0-NNuY', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 1, 'vicinity': 'House Of 265, Behind Gayatri Mandir, Samata Colony, Samata Colony, Raipur'}, {'geometry': {'location': {'lat': 21.243796, 'lng': 81.6363779}, 'viewport': {'northeast': {'lat': 21.24520442989272, 'lng': 81.63770307989272}, 'southwest': {'lat': 21.24250477010728, 'lng': 81.63500342010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'e0b76eed666f497cb0558cd4b438aaf1c78663ee', 'name': 'Bharat Petroleum', 'photos': [{'height': 1080, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/114688963882099614778">Ranjesh Kumar</a>'], 'photo_reference': 'CmRaAAAAuGev_8Uh17EhFDjMOTiB-JIzHHq2obpvKLwRdbdLH6TL6b-8gtKwJdF9lXH20IG5He3h2lz5WRuUoTGBOHNMgiFK5MUEtskcLVgX4PxMpeZzKTCKeSYRouZ5EoaLpK_vEhC_QpUkhzkeKD9RppkRwD34GhQHK_BA2renWVKaqjBtOVoFpmi1Qw', 'width': 1920}], 'place_id': 'ChIJP1z2_5fdKDoRYk8CSf8BqqI', 'plus_code': {'compound_code': '6JVP+GH Raipur, Chhattisgarh', 'global_code': '7MH36JVP+GH'}, 'rating': 3.8, 'reference': 'ChIJP1z2_5fdKDoRYk8CSf8BqqI', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 82, 'vicinity': 'Great Eastern Rd, Ganeshram Nagar, Raipur'}, {'geometry': {'location': {'lat': 21.2437574, 'lng': 81.6363519}, 'viewport': {'northeast': {'lat': 21.24517567989272, 'lng': 81.63766582989271}, 'southwest': {'lat': 21.24247602010728, 'lng': 81.63496617010726}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'd2f3c83d1ca35d71d85a43f48abad94d0d70e564', 'name': 'BP Petrol Bunk', 'place_id': 'ChIJ32T7_5fdKDoRC7N74rB533g', 'plus_code': {'compound_code': '6JVP+GG Raipur, Chhattisgarh', 'global_code': '7MH36JVP+GG'}, 'rating': 0, 'reference': 'ChIJ32T7_5fdKDoRC7N74rB533g', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 0, 'vicinity': 'Ganeshram Nagar, Byron Bazar, Raipur'}, {'geometry': {'location': {'lat': 21.2517542, 'lng': 81.6411974}, 'viewport': {'northeast': {'lat': 21.25306007989272, 'lng': 81.64245652989273}, 'southwest': {'lat': 21.25036042010728, 'lng': 81.63975687010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'ec8cc44b46031b00b252c0012b032b6fda0a95b8', 'name': 'Aastha Fuels', 'opening_hours': {'open_now': True}, 'photos': [{'height': 2592, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/117409221616875047576">Hoosain Narker</a>'], 'photo_reference': 'CmRaAAAA_0wwDFlUY5g0Eet-Nhap4IMhn4mZkKaP0GwHrFmrdO6vrrkZcWO5NG3ZcPd988mzNBdeAViTTo11xiSiNRlW4Y-4XIU9Ke-G7wjg7EXRYz2gQ5eM8o5qpt562Mj9s5etEhBDEY_hs1RyZDYcAqqj7KKaGhSKGku9Jq2dIh1yOiSTgv9n5xuOCw', 'width': 4608}], 'place_id': 'ChIJb0ABjpvdKDoRrbSmnCGNur4', 'plus_code': {'compound_code': '7J2R+PF Raipur, Chhattisgarh', 'global_code': '7MH37J2R+PF'}, 'rating': 3.7, 'reference': 'ChIJb0ABjpvdKDoRrbSmnCGNur4', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 19, 'vicinity': 'Devendra Nagar, Raipur'}, {'geometry': {'location': {'lat': 21.251753, 'lng': 81.6412631}, 'viewport': {'northeast': {'lat': 21.25304647989272, 'lng': 81.64249662989273}, 'southwest': {'lat': 21.25034682010727, 'lng': 81.63979697010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '91ed8adc083748d500d5e8bca1255cd0768703b7', 'name': 'HP PETROL PUMP', 'opening_hours': {'open_now': True}, 'photos': [{'height': 1341, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/108784518866737615628">Muskan Parihar</a>'], 'photo_reference': 'CmRaAAAAwgo-jIni2yD-UawYephUjQpCdgRSmEbb-nGdCpLufb2OoCbkApYb7195YOqnmZ2yMu20uy7DFjvwG6RvJ2HpS1W00TDMtlLSFNFBVGwl1yBdQEfOsGLH9JB8W7tTcIUfEhAeQXmD5K-pqwWdYMQedv9KGhR55taSYC2e3Os9djrNYkH0VGpkLw', 'width': 1679}], 'place_id': 'ChIJL6dwjpvdKDoRQk1hTWwcebg', 'plus_code': {'compound_code': '7J2R+PG Devendra Nagar, Raipur, Chhattisgarh', 'global_code': '7MH37J2R+PG'}, 'rating': 3.3, 'reference': 'ChIJL6dwjpvdKDoRQk1hTWwcebg', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 32, 'vicinity': 'Jail Rd, Devendra Nagar, Raipur'}, {'geometry': {'location': {'lat': 21.24576, 'lng': 81.64059}, 'viewport': {'northeast': {'lat': 21.24715012989272, 'lng': 81.64205207989272}, 'southwest': {'lat': 21.24445047010728, 'lng': 81.63935242010727}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '7925659125dcc5687058ec5d7aef3f7a015f05bf', 'name': 'HP PETROL PUMP - ANOOP AUTO SERVICES', 'opening_hours': {'open_now': True}, 'photos': [{'height': 1840, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/115847946694899531286">hari puri</a>'], 'photo_reference': 'CmRaAAAAsjf7Qh262vQwL8P-nIqOTVcq1mJLC9y8V7gHW69A1GZotcr586arpgIjkzDz-ZdiXyxEihT8OVdNDPEStXWAkpyoD4ERFhsE-oY3m8vyQKhrEa55-yJwlYUrus7rGE3SEhB4vx3oix_zmpvu_lX8dIcMGhRMhZeJVKZBNvD_xg8xncI1IWyFBQ', 'width': 3280}], 'place_id': 'ChIJS_CMwZjdKDoRgTeUShOpmuQ', 'plus_code': {'compound_code': '6JWR+86 Raipur, Chhattisgarh', 'global_code': '7MH36JWR+86'}, 'rating': 3.5, 'reference': 'ChIJS_CMwZjdKDoRgTeUShOpmuQ', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 13, 'vicinity': 'HPC Dealer G.E. Road, OPP Secretariate Post & Dist. (CG), Raipur'}, {'geometry': {'location': {'lat': 21.245662, 'lng': 81.640689}, 'viewport': {'northeast': {'lat': 21.24693847989272, 'lng': 81.64204587989272}, 'southwest': {'lat': 21.24423882010727, 'lng': 81.63934622010729}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': 'f552ce674afe3f5eaca047fa6eae9b73bef0996e', 'name': 'Club HP', 'place_id': 'ChIJfSeay5jdKDoRc-DULUASr2o', 'plus_code': {'compound_code': '6JWR+77 Raipur, Chhattisgarh', 'global_code': '7MH36JWR+77'}, 'rating': 2.8, 'reference': 'ChIJfSeay5jdKDoRc-DULUASr2o', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 4, 'vicinity': 'Mantalay Shashtri Chowk, Raipur'}, {'geometry': {'location': {'lat': 21.2396833, 'lng': 81.62713330000001}, 'viewport': {'northeast': {'lat': 21.24092867989272, 'lng': 81.62845082989271}, 'southwest': {'lat': 21.23822902010728, 'lng': 81.62575117010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '3f13daec9c2fa8aadce255b626f38c52cc5007f1', 'name': 'Alterantive Fuel', 'place_id': 'ChIJAQ_fDb_dKDoRAw8Wwyb_n2w', 'rating': 5, 'reference': 'ChIJAQ_fDb_dKDoRAw8Wwyb_n2w', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 1, 'vicinity': '16/512, Azad Chowk, G E Road, Azad Chowk, Raipur'}, {'geometry': {'location': {'lat': 21.2458224, 'lng': 81.6416426}, 'viewport': {'northeast': {'lat': 21.24717257989272, 'lng': 81.64302622989273}, 'southwest': {'lat': 21.24447292010727, 'lng': 81.64032657010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '0800bab8ff45d9b6a70001a42f1eff08e45001bf', 'name': 'Chawla Service station', 'opening_hours': {'open_now': True}, 'place_id': 'ChIJIdGIy5jdKDoR79MbwkjAWWg', 'plus_code': {'compound_code': '6JWR+8M Raipur, Chhattisgarh', 'global_code': '7MH36JWR+8M'}, 'rating': 3.3, 'reference': 'ChIJIdGIy5jdKDoR79MbwkjAWWg', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 3, 'vicinity': 'Jail Rd, Kutchery Chowk, Raipur, Moudhapara, Raipur'}, {'geometry': {'location': {'lat': 21.2456735, 'lng': 81.6416095}, 'viewport': {'northeast': {'lat': 21.24701732989272, 'lng': 81.64299942989273}, 'southwest': {'lat': 21.24431767010728, 'lng': 81.64029977010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '4294b74699a7d7e250f77c279e5b2ef636392e74', 'name': 'HP Petrol Pump - Chawla Service Station', 'opening_hours': {'open_now': True}, 'photos': [{'height': 4160, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/112890785733188340943">rameshwar kumar Sahu</a>'], 'photo_reference': 'CmRaAAAA6puWDFyOIVGlT5RKuhmmLXSv1VVXLv5Q1INNDCRFCrP_rCVzVjWgHjPLSYbYbVxynuwLDFq7tzkuapWVhTxzzMSlCF1M84h1CQHVSmlKRRZYR2NusDy1aD-M0LmnLnbNEhB_KmAcih_BpKcFqUWP8NBaGhSZKCntjvZOlj3gCGM6i-Z2Tk3RgQ', 'width': 3120}], 'place_id': 'ChIJKdT7y5jdKDoRoRvW1ul5kHw', 'plus_code': {'compound_code': '6JWR+7J Raipur, Chhattisgarh', 'global_code': '7MH36JWR+7J'}, 'rating': 3.7, 'reference': 'ChIJKdT7y5jdKDoRoRvW1ul5kHw', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 233, 'vicinity': 'OPP. Secretariate Shastri Chowk'}, {'geometry': {'location': {'lat': 21.243007, 'lng': 81.615011}, 'viewport': {'northeast': {'lat': 21.24425952989272, 'lng': 81.61632602989272}, 'southwest': {'lat': 21.24155987010728, 'lng': 81.61362637010728}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/gas_station-71.png', 'id': '860bb3929e99db9c5f8152d4aa2fff8a4184ec2a', 'name': 'Bharat Petroleum', 'opening_hours': {'open_now': True}, 'photos': [{'height': 3456, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/102773039998208852339">Archit7Ojha</a>'], 'photo_reference': 'CmRaAAAANMPfYG4v3XjfuVSA8_CYqHI5HByXMgrdGTnc52wE-ygCCx8oPRahDcUJENvAKeZKYsJCh7ANMIZnbpPVXMJMjLXTN0nVtLrWyQpBpUjoxlb2IBd6FFThQLZzs0CeRXW9EhDvodK47VU233QaXX8cXg7ZGhTck0HmvP_KDRoTn0sZrOg48sur_w', 'width': 4608}], 'place_id': 'ChIJYbJ7A-jdKDoRetdX40gmD1g', 'plus_code': {'compound_code': '6JV8+62 Raipur, Chhattisgarh', 'global_code': '7MH36JV8+62'}, 'rating': 3.7, 'reference': 'ChIJYbJ7A-jdKDoRetdX40gmD1g', 'scope': 'GOOGLE', 'types': ['gas_station', 'point_of_interest', 'establishment'], 'user_ratings_total': 323, 'vicinity': 'Great Eastern Rd, Opposite Raj Kumar College, Choubey Colony, Ramkund, Raipur'}]
		

		
		res = {}
		# keep looping upto length of y
		# print('The closest petrol pump is:- ', y[0]['name'])
		# print('The list of petrol pumps in ascending order is:- ')
		for i in range(len(y)): 
			print(y[i]['name'])
			petrol_pump = PetrolPump.objects.filter(name=y[i]["name"])
			if not petrol_pump:
				petrol_pump = PetrolPump(
					name=y[i]['name'],
					rating=0.0,
					number=0,
					GRating=y[i]['rating']
				)
				petrol_pump.save()
			else:
				petrol_pump = petrol_pump[0]
			print(petrol_pump)
			res[i]={
				'location': y[i]['geometry']['location'],
				'name': y[ i]['name'],
				'rating': y[i ]['rating'],
				'Total_user_ratings': y[i]['user_ratings_total'],
				'Area': y[ i]['vicinity'],
				'app_ratings': petrol_pump.rating
			}
			# print(pumps_json[i])

		# Dumping ot a json file

		# print(pumps_json)

		
		return JsonResponse(res)

def petrol_pump_ratings_response(request):
	if request.method =="POST":
		petrol_pump = PetrolPump.objects.get(name=request.POST["name"])
		print(petrol_pump)
		s = petrol_pump.rating * petrol_pump.number
		petrol_pump.rating = ((float( s) + int(request.POST["rating"]))/(petrol_pump.number + 1))

		petrol_pump.number += 1

		print(petrol_pump)
		petrol_pump.save()

		response = {
			"success": True
		}

		return JsonResponse(response)

def CurrentStats(request):
	if request.method == "POST":
		token = request.POST['token']
		user = UserAccount.objects.get(token=token)
		currentData = CurrentData.objects.get(user=user)
		resposeObject = {
			'success':True,
			'mileage':currentData.totalDistance/currentData.petrolConsumed,
			'distance':currentData.totalDistance
		}
		print('answer',resposeObject)
		return JsonResponse(resposeObject)


def travelTime(request):
	lat1 = request.POST['lat1']
	lon1 = request.POST['lon1']
	lat2 = request.POST['lat2']
	lon2 = request.POST['lon2']
	baseURL = 'https://www.google.com/search?'
	add = 'q=distance+from+'+lat1+'%2C+'+lon1+'+to+'+lat2+'%2C+'+lon2
	r = requests.get(baseURL+add)
	data = r.content
	soup = BeautifulSoup(data, 'lxml')
	mydivs = soup.findAll("span", {"class": "FCUp0c"})
	if mydivs == []:
		return JsonResponse({
			'success':False
		})
	else:
		time = mydivs[0].text
		time = time.strip().split(' ')
		time = float(time[0])+time[2]/60
		print("time",time)
		return JsonResponse({
			'success':True,
			'time':time
		})
