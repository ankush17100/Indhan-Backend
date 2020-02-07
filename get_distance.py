import requests, json
# sample URl
'''http://dev.virtualearth.net/REST/V1/Routes/driving?wp.0=Eiffel%20Tower&wp.1=louvre%20museum&optmz=distance&output=json&key=AnoFWgh2sc2G9nPxrPl-LZbLy8gEI-7kMuCl9yjaknj1HFpk1gxiwVb9Fy580CuJ'''
key = 'AnoFWgh2sc2G9nPxrPl-LZbLy8gEI-7kMuCl9yjaknj1HFpk1gxiwVb9Fy580CuJ'

def get_distance(coord1:str, coord2:str, driving_mode = 'driving', key='AnoFWgh2sc2G9nPxrPl-LZbLy8gEI-7kMuCl9yjaknj1HFpk1gxiwVb9Fy580CuJ'):
    '''
    Returns the response JSON that is returned from the API

    docs of the API can be found at https://docs.microsoft.com/en-us/bingmaps/rest-services/routes/calculate-a-route and functions nd arguments can be manipulated accordingly
    
    Parameters:
    coord1(str): it should contain latitude and longitude as lat, lon of the start position. It can also contain the location address string where the whitespaces whould be replace by                     '%20' for example 'eiffel tower' should be replaced by eiffel%20tower

    coord2(str): it should contain latitude and longitude as lat, lon of the end position. It can also take in the location address same as coord2

    driving_mode(str): [Optional] The mode of travel for the route. One of the following values:
                                    Driving(default for the API as well as the function)
                                    Walking
                                    Transit
    
    key(str): The key for the API
    '''
    URL = 'http://dev.virtualearth.net/REST/V1/Routes/' + driving_mode + '?wp.0=' + coord1 + '&wp.1=' + coord2 + '&output=json' + '&key=' + key
    r = requests.get(URL)
    x = r.json()
    return x


coord1 = '21.1284644,81.7639714'
coord2 = '21.2497222,81.6028351'
result = get_distance(coord1, coord2)

# Extracting the main things that we want from the JSON response
result_trimmed = {'trafficcongestion': result['resourceSets'][0]['resources'][0]['trafficCongestion'],
                     'trafficdataused': result['resourceSets'][0]['resources'][0]['trafficDataUsed'],
                     'traveldistance': result['resourceSets'][0]['resources'][0]['travelDistance'],
                     'travelduration': result['resourceSets'][0]['resources'][0]['travelDuration'],
                     'traveldurationtraffic': result['resourceSets'][0]['resources'][0]['travelDurationTraffic']}

print(result_trimmed)