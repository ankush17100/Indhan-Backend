# AIzaSyB76e5KFCFlE66xXtLg80jA7677k53Gcxs
# Python program to get a set of  
# places according to your search  
# query using Google Places API 
  
# importing required modules 
import requests, json 
  
# enter your api key here 
api_key = 'AIzaSyB76e5KFCFlE66xXtLg80jA7677k53Gcxs'
  
# url variable store url 
url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
  
# The text string on which to search 
keyword = input('Search query: ') 
# Enter coordinates here

# TODO
# Enter code to put coordinates here
coordinates = '21.2544787,81.6051032'
radius = '50000'

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
  
# keep looping upto length of y
print('The closest petrol pump is:- ', y[0]['name'])
print('The list of petrol pumps in ascending order is:- ')
for i in range(len(y)): 
      
    # Print value corresponding to the 
    # 'name' key at the ith index of y 
    print(y[i]['name'])
print(URL)
# print('\ny', y)
# print('\nx', x)
# print('y type', type(y))
# print('y[0] type', type(y[0]))
# print('x - type', type(x))
pumps_json = {}
for i in range(len(y)):
    pumps_json[i] = {'location': y[i]['geometry']['location'], 'name': y[i]['name'], 'rating': y[i]['rating'], 'Total_user_ratings': y[i]['user_ratings_total'], 'Area': y[i]['vicinity']}
    print(pumps_json[i])

# Dumping ot a json file


with open('pumps_json.json', 'w') as json_file:
  json.dump(pumps_json, json_file)