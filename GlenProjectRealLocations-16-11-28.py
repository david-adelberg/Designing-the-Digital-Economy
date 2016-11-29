
# coding: utf-8

# In[1]:

import numpy as np
import itertools as it
import matplotlib.pyplot as plt


# ### Part 1: ###
# Convert uberIncomesRaw and carCost in the following cell to valuations per minute, or per mile (depending on usage of Google Distance Matrix API)

# In[2]:

# Median Uber user has an income of approximately $71,000
# 40% of Uber passengers make at least $100,000
# from http://uctc.net/research/papers/UCTC-FR-2014-08.pdf
# I added some high earning users, and the result is an
# approximate user distribution of incomes in 2014:

uberIncomesRaw = [25.0, 50.0, 85.0, 150.0, 300.0, 600.0]
uberIncomesDistRaw = [8.0,23.0,18.0,27.0,9.0, 2.0] 
# Note that this doesn't sum to 100, because about 20% of uber drivers
# declined to share their income with the surveyors

uberIncomes = uberIncomesRaw/(np.ones(len(uberIncomesRaw)))
# Note that these numbers are not normalized in any way
# In production, these numbers should be in units of $/minute

uberIncomesDist = uberIncomesDistRaw/np.sum(uberIncomesDistRaw)
# Force probabilities to sum to 1.

default_num_locations=5

timeValues = np.random.choice(uberIncomes, default_num_locations, p=uberIncomesDist)
# (David) we need to normalize this.

#Estimated car value of time to be equivalent to 15K/year earner
carCost = 15

timeValues = np.append(carCost, timeValues)


# ### Part 2: ###
# 
# Request user input of destinations, including an origin point and a number of dropoff points. Then, convert these destinations to two-dimensional coordinates and return them as: $$[(originx,originy,0.0),(x_1,y_1,1.0),(x_2,y_2,2.0),...]$$
# 
# At this stage, it would be OK if we just get something fairly reasonable that we can feed to Google Maps and use to check the rest of the results; but in theory we should be able to type in or somehow input destinations.
# To simulate user input, we took a list of sample locations from Chicago in latitude/longitude coordinates, and found a random subset of $n$ locations where $n$ is the number of riders. We then used Google Maps API to assign those lat/long coordinates to street addresses across Chicago.

# In[3]:

def readInputLocations(fileName): # filename is an input file which is a list of lat/long coordinates separated by new lines
    array = []
    with open(fileName, "r") as inputs:
        for line in inputs:
            location=line.split(",");
            for i in range (len(location)):
                location[i] = location[i].strip()
                location[i] = float(location[i])
            array.append(location)
    return array


# In[4]:

from random import randint
def randomLocations(locationArray, numLocations):
    arrayIndexes = []
    randomLocationArray = []
    chicagoOHare = [41.9742,-87.9073] # location of OHare Airport
    randomLocationArray.append(chicagoOHare); # origin point
    for i in range(numLocations):
        x = randint(0,len(locationArray)-1)
        while x in arrayIndexes:
            x = randint(0,len(locationArray)-1)
        arrayIndexes.append(x)
    for index in arrayIndexes:
        randomLocationArray.append(locationArray[index])
    return randomLocationArray


# ### Part 3: ###
# Use the destinations to make a Google Distance Matrix API using all of our destinations (notice that you'll have to strip out the indexing of the locations) as both origin and destination points (so if there are $n$ destinations, the output should be an $n+1 \times n+1$ matrix). Also it would be great if the returned matrix could just be floats representing the number of minutes between locations; see if parsing is easy. Make sure that the order of things is preserved.

# In[5]:

import requests
import json
def sendRequest(locationArray): # google request
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


# In[6]:

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


# In[7]:

def getDurationMatrix(response): # duration matrix in seconds
	return getMatrix(response,"duration")


# In[8]:

def getDistanceMatrix(response): # creates a distance matrix in meters
	return getMatrix(response,"distance")


# In[9]:

def get_info_from_inputs(num_locations=default_num_locations, locationFile='locations.txt'):
    inp_locations = readInputLocations(locationFile)
    processed_array = randomLocations(inp_locations, num_locations)
    response = sendRequest(processed_array)
    addresses = response["origin_addresses"]
    durMatrix = getDurationMatrix(response)
    distMatrix = getDistanceMatrix(response)
    return addresses, processed_array, durMatrix, distMatrix


# In[ ]:




# In[ ]:




# The below code is slightly modified from the version in the abstract locatiosn to reflect that our list of destinations will look like $$[origin, loc_1, loc_2, \ldots]$$

# In[10]:

def pathList(destinations):
    perms = it.permutations(destinations[1:len(destinations)])
    origin = destinations[0]
    lst = list(perms)
    np.random.shuffle(lst)

    #To reduce computation time in the case of a large number of riders,
    #We simply look at some large subset of paths instead of the entire space
    #Obviously this isn't great in the worst case, but it is good in the average case
    if len(lst) > 120:
        lst = lst[:120]
    permlist = []
    for x in lst:
        newpath = []
        newpath.append(origin)
        for j in x:
            newpath.append(j)
        permlist.append(newpath)

    return permlist

def subsetPathList(destinations, leftOut):
    subDests = []
    for x in destinations:
        if x[2] != leftOut:
            subDests.append(x)
            
    return pathList(subDests)


# This code is copied from the abstract location version; nothing has changed.

# In[11]:

# Compute the cost of a given path given a distance matrix
# containing pairwise distances between points in the path
def costMat(weights, path, distances):
    currloc = path[0]
    currcost = 0
    for x in path:
        currcost += weights[x[2]]   
    totalcost = 0
    for i in range(len(path)):
        totalcost += currcost * distances[currloc[2]][path[i][2]]
        if i > 0:
            currcost = currcost - weights[path[i][2]]
        currloc = path[i]
    return totalcost

# Compute the environmental cost of the path, equal to
# the cost of the path to the car
def envCostMat(path, distances):
    currloc = path[0]
    currcost = carCost
    totalcost = 0
    for i in range(len(path)):
        if i > 0:
            totalcost += currcost * distances[currloc[2]][path[i][2]]
            currloc = path[i]
    return totalcost

# Computes the individual costs of a given path and returns a matrix
# with the respective costs formatted as [car, 0, 1, . . . ]
def indivCostMat(weights, path, distances):
    numPeople = len(weights)
    costs = np.zeros(numPeople)
    currloc = path[0]
    totalcost = 0
    inCar = set()
    inCar.add(0)
    for n in range(len(path)):
        inCar.add(path[n][2])
    for i in range(len(path)):
        for j in inCar:
            costs[j] += weights[j]*distances[currloc[2]][path[i][2]]
            
        if i > 0: #Never removes the car
            inCar.remove(path[i][2])
        currloc = path[i]
    return costs

def optimalPath(weights, paths, distances):
    wgtcost = []
    for i in range(len(paths)):
        wgtcost.append(costMat(weights,paths[i],distances))
    
    optimal = wgtcost.index(min(wgtcost))
    return optimal

def shortestPath(paths,distances):
    unwgtcost = []
    for i in range(len(paths)):
        unwgtcost.append(envCostMat(paths[i],distances))
    
    shortest =  unwgtcost.index(min(unwgtcost))
    return shortest


# This code is unique to calculating payments, and is unfinished. I think it works as desired, although you may want to compare and experiment with the less polished code in the GlenProject-16-11-13 file to make sure that this does what you want.

# In[12]:

#def transform_path_list(path_list):
#    return [[(val, 0, i) for i, val in enumerate(path)] for path in path_list]


# In[44]:

def harmMatrices(timeValues, destinations, distMatrix):
    #distMatrix = distanceMatrix(destinations)
    allPaths = pathList(destinations)
    #allPaths = transform_path_list(allPaths)
    optPath = optimalPath(timeValues,allPaths,distMatrix)
    shortPath = shortestPath(allPaths,distMatrix)
    shortPath = allPaths[shortPath]
    print(optPath)
    optPath = allPaths[optPath]
    deficientPaths = []
    for i in range(len(timeValues)):
        if i > 0:
            deficientPaths.append(subsetPathList(destinations,i))
    subOptCosts = []
    subOptPaths = []
    subOptPaths.append(shortPath)
    #first element of path list is shortest path
    subOptPaths.append(optPath)
    #second element of path list is optimal path
    subOptCosts.append(indivCostMat(timeValues,optPath,distMatrix))
    for i in range(len(timeValues)-1):
        deficientOptPath = deficientPaths[i][optimalPath(timeValues,deficientPaths[i],distMatrix)]
        subOptPaths.append(deficientOptPath)
        #remaining elements of path list will be optimal paths leaving out one rider
        subOptCosts.append(indivCostMat(timeValues, deficientOptPath,distMatrix))
    output = []
    output.append(subOptCosts[0])
    for i in range(len(timeValues)):
        if i > 0:
            payments = subOptCosts[0]-subOptCosts[i]
            payments[i] = 0
            output.append(payments)
        
    return output, subOptPaths, subOptCosts


# In[79]:

addresses, lat_longs, durMatrix, distMatrix = get_info_from_inputs()


# In[80]:

lat_longs


# In[81]:

#rerandomize timevalues

timeValues = np.random.choice(uberIncomes, default_num_locations, p=uberIncomesDist)

carCost = 15

timeValues = np.append(carCost, timeValues)


timeValues


# In[82]:


destinations = [(dest[0], dest[1], i) for i, dest in enumerate(lat_longs)]


# In[83]:

destinations


# In[84]:

#timeValues = np.insert(timeValues,0,0)


# In[85]:

len(timeValues), len(destinations), len(distMatrix)


# In[86]:

output, paths, costs = harmMatrices(timeValues, destinations, durMatrix)
#output, paths, costs = harmMatrices(np.ones(len(destinations)), destinations, durMatrix)


# In[87]:

costs


# In[89]:

paths


# In[94]:

durMatrix


# In[90]:

np.divide(output,3600.0)


# In[91]:

for i in range(len(output)): 
    if i == 0:
        print "Total cost to passengers is ", output[i]/3600.0
    else:
        print "Marginal impact of rider ", i, "= ", output[i]/3600.0


# ### Part 4: ###
# 
# Basically what remains to be done is to turn this output (marginal impact of riders) into a payment scheme. To that end, please read a paper about Vickrey Clarke Groves mechanisms and make sure that you know and can defend the answers to the following questions: 
# 
# 1. What is the right way to compute payments in a VCG auctions?
# 2. What does the mechanism do with those payments?
# 
# Then, find a way to use the harmMatrices (which will have units of dollars after the Distance Matrix API stuff is implemented) to compute appropriate payments from each participant. Try to see if these payments are reasonable, and if they are not, to figure out what we are doing wrong.
# 

# In[92]:

payments = [np.sum(oput) / 3600.0 for oput in output[1:]] # Still seems large


# In[93]:

payments


# In[28]:

timeValues


# """
# def harmMatrices(timeValues, destinations, distMatrix):
#     #distMatrix = distanceMatrix(destinations)
#     allPaths = pathList(destinations)
#     
#     allPaths = transform_path_list(allPaths)
#     
#     optPath = allPaths[optimalPath(timeValues,allPaths,distMatrix)]
#     #deficientPaths = []
#     
#     # I rewrote this, since your original code seems to have forgotten to deal with other variables.
#     #for i in range(len(timeValues)):
#         #deficientPaths.append(subsetPathList(destinations,i))
#     subOptCosts = []
#     
#     #deficientPaths = transform_path_list(deficientPaths)
#     
#     for i in range(len(timeValues)):
#         # I think this is what you meant to do in your code?
#         dTimeValues = timeValues#np.delete(timeValues, i) #timeValues[:i] + timeValues[i+1:]
#         dDeficientPaths = allPaths[:i] + allPaths[i+1:]
#         dDistMatrix = distMatrix[:i] + distMatrix[i+1:]
#         dDistMatrix = [val[:i] + val[i+1:] for val in dDistMatrix]
#         
#         pth = optimalPath(dTimeValues,dDeficientPaths,dDistMatrix)
#         
#         #deficientPaths.append(pth) This would be the most logical reinterpretation of your code
#         #This interpretation has the issue that I removed the ith element, so the index isn't that useful.
#         # I don't calculate it.
#         
#         #deficientOptPath = deficientPaths[i][pth] I also reinterpret here
#         
#         deficientOptPath = dDeficientPaths[pth]
#         
#         subOptCosts.append(indivCostMat(timeValues, deficientOptPath,distMatrix))
#     output = []
#     output[0] = subOptCosts[0]
#     for i in range(len(timeValues)):
#         if i > 0:
#             payments = subOptCosts[0]-subOptCosts[i]
#             payments[i] = 0
#             output[i] = payments
#         
#     return output
# """
