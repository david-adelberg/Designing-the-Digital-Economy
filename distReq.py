import requests
import json
from random import randint


def readInputLocations(fileName):
	array = []
	with open(fileName, "r") as inputs:
	    for line in inputs:
	    	location=line.split(",");
	    	for i in range (len(location)):
	    		location[i] = location[i].strip()
	    		location[i] = float(location[i])
	        array.append(location)
	return array

def randomLocations(locationArray, numLocations):
	arrayIndexes = []
	randomLocationArray = []
   chicagoOHare = [41.9742,-87.9073]
   randomLocationArray.append(chicagoOHare) # origin point
	for i in range(numLocations):
		x = randint(0,len(locationArray)-1)
		while x in arrayIndexes:
			x = randint(0,len(locationArray)-1)
		arrayIndexes.append(x)
	for index in arrayIndexes:
		randomLocationArray.append(locationArray[index])
	return randomLocationArray


# def sendRequest(): # mapbox, for reference purposes only
# 	url = "https://api.mapbox.com/distances/v1/mapbox/driving"
# 	querystring = {"access_token":"pk.eyJ1IjoiYWxhbmxpdSIsImEiOiJjaWsxaTFnNm0zOXFqdmdsejUxaXVvbnA2In0.ZtiuHVLRb2IOKT9qY8VQmA"}

# 	coordinates = readInputLocations(locationFile)
# 	payload = "{ \"coordinates\": "+ str(coordinates)+ " }"

# 	headers = {
# 	    'content-type': "application/json",
# 	    'cache-control': "no-cache",
# 	    'postman-token': "93701ef9-42d2-1e63-0524-4219a8f57fa9"
# 	    }
# 	response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

# 	print(response.text)


def sendRequest(locationArray): # google
	apiKey = "AIzaSyD0NJrqsnsTz6unHq4d2FqF2kbhDxYih0Y"
	url = "https://maps.googleapis.com/maps/api/distancematrix/json"

	locations = ""

	for location in locationArray:
		for coord in location:
			locations+= str(coord)
			locations+= ","
		locations = locations[:-1] #strip comma
		locations += "|"

	locations = locations[:-1] # strip the last |

	querystring = {"origins":locations, "destinations": locations, "mode": "driving", "language":"en-US", "key" : apiKey}

	response = requests.request("GET", url, params=querystring)
	# print(response.text)
	json_response = json.loads(response.text)
	return json_response

def getMatrix(response, types):
	numLocations = len(response["rows"])
	matrix= []
	for i in range(numLocations):
		newRow = []
		for j in range(numLocations):
			newRow.append(0)
		matrix.append(newRow)

	for i in range(numLocations): # i is origin, j is destination
		for j in range(numLocations):
			matrix[i][j] = response["rows"][i]["elements"][j][types]["value"]
	return matrix

def getDurationMatrix(response): # duration matrix in seconds
	return getMatrix(response,"duration")

def getDistanceMatrix(response): # creates a distance matrix in meters
	return getMatrix(response,"distance")

def getIndex(location, addresses):
   return addresses.index(location)

# USAGE EXAMPLE

# import distReq # uncomment this when using in another file

numRiders = 5
locationFile = "locations.txt" # stores all the lat/longs on different lines

processedArray = randomLocations(readInputLocations(locationFile), numRiders)
response = sendRequest(processedArray)

addresses = response["origin_addresses"] # list of length numLocations of the addresses
durMatrix = getDurationMatrix(response)
distMatrix = getDistanceMatrix(response)

# There is a 1:1 mapping between locations and their array index, so to make it easier, we can search by address
# example: durMatrix[getIndex("2627 S Drake Ave, Chicago, IL 60623, USA", addresses), getIndex("E Lake Service St, Chicago, IL 60601, USA", addresses)]





'''  EXAMPLE RESPONSE BELOW
{
   "destination_addresses" : [
      "2627 S Drake Ave, Chicago, IL 60623, USA",
      "3538 S Francisco Ave, Chicago, IL 60632, USA",
      "350 West Mart Center, Chicago, IL 60654, USA",
      "E Lake Service St, Chicago, IL 60601, USA",
      "319-505 E Illinois St, Chicago, IL 60611, USA"
   ],
   "origin_addresses" : [
      "2627 S Drake Ave, Chicago, IL 60623, USA",
      "3538 S Francisco Ave, Chicago, IL 60632, USA",
      "350 West Mart Center, Chicago, IL 60654, USA",
      "E Lake Service St, Chicago, IL 60601, USA",
      "319-505 E Illinois St, Chicago, IL 60611, USA"
   ],
   "rows" : [
      {
         "elements" : [
            {
               "distance" : {
                  "text" : "1 m",
                  "value" : 0
               },
               "duration" : {
                  "text" : "1 min",
                  "value" : 0
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "3.2 km",
                  "value" : 3186
               },
               "duration" : {
                  "text" : "9 mins",
                  "value" : 518
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "12.4 km",
                  "value" : 12399
               },
               "duration" : {
                  "text" : "22 mins",
                  "value" : 1312
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "14.1 km",
                  "value" : 14054
               },
               "duration" : {
                  "text" : "21 mins",
                  "value" : 1271
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "14.1 km",
                  "value" : 14112
               },
               "duration" : {
                  "text" : "21 mins",
                  "value" : 1264
               },
               "status" : "OK"
            }
         ]
      },
      {
         "elements" : [
            {
               "distance" : {
                  "text" : "3.5 km",
                  "value" : 3497
               },
               "duration" : {
                  "text" : "10 mins",
                  "value" : 594
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "1 m",
                  "value" : 0
               },
               "duration" : {
                  "text" : "1 min",
                  "value" : 0
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "12.1 km",
                  "value" : 12085
               },
               "duration" : {
                  "text" : "23 mins",
                  "value" : 1368
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "14.6 km",
                  "value" : 14637
               },
               "duration" : {
                  "text" : "18 mins",
                  "value" : 1105
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "14.8 km",
                  "value" : 14783
               },
               "duration" : {
                  "text" : "18 mins",
                  "value" : 1108
               },
               "status" : "OK"
            }
         ]
      },
      {
         "elements" : [
            {
               "distance" : {
                  "text" : "15.7 km",
                  "value" : 15693
               },
               "duration" : {
                  "text" : "21 mins",
                  "value" : 1237
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "14.2 km",
                  "value" : 14195
               },
               "duration" : {
                  "text" : "17 mins",
                  "value" : 1019
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "1 m",
                  "value" : 0
               },
               "duration" : {
                  "text" : "1 min",
                  "value" : 0
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "2.4 km",
                  "value" : 2432
               },
               "duration" : {
                  "text" : "9 mins",
                  "value" : 543
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "1.9 km",
                  "value" : 1871
               },
               "duration" : {
                  "text" : "8 mins",
                  "value" : 456
               },
               "status" : "OK"
            }
         ]
      },
      {
         "elements" : [
            {
               "distance" : {
                  "text" : "15.8 km",
                  "value" : 15750
               },
               "duration" : {
                  "text" : "20 mins",
                  "value" : 1179
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "14.3 km",
                  "value" : 14252
               },
               "duration" : {
                  "text" : "16 mins",
                  "value" : 962
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "1.9 km",
                  "value" : 1860
               },
               "duration" : {
                  "text" : "8 mins",
                  "value" : 464
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "1 m",
                  "value" : 0
               },
               "duration" : {
                  "text" : "1 min",
                  "value" : 0
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "1.1 km",
                  "value" : 1087
               },
               "duration" : {
                  "text" : "4 mins",
                  "value" : 263
               },
               "status" : "OK"
            }
         ]
      },
      {
         "elements" : [
            {
               "distance" : {
                  "text" : "15.7 km",
                  "value" : 15662
               },
               "duration" : {
                  "text" : "19 mins",
                  "value" : 1141
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "14.2 km",
                  "value" : 14164
               },
               "duration" : {
                  "text" : "15 mins",
                  "value" : 923
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "2.1 km",
                  "value" : 2131
               },
               "duration" : {
                  "text" : "7 mins",
                  "value" : 419
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "1.6 km",
                  "value" : 1579
               },
               "duration" : {
                  "text" : "4 mins",
                  "value" : 242
               },
               "status" : "OK"
            },
            {
               "distance" : {
                  "text" : "1 m",
                  "value" : 0
               },
               "duration" : {
                  "text" : "1 min",
                  "value" : 0
               },
               "status" : "OK"
            }
         ]
      }
   ],
   "status" : "OK"
}
'''
