import numpy as np
import itertools as it
# import matplotlib.pyplot as plt

# The below code is slightly modified from the version in the abstract locatiosn to reflect that our list of destinations will look like $$[origin, loc_1, loc_2, \ldots]$$

# In[11]:

def pathList(destinations):
    perms = it.permutations(destinations[1:len(destinations)])
    origin = destinations[0]
    lst = list(perms)
    # np.random.shuffle(lst)

    #To reduce computation time in the case of a large number of riders,
    #We simply look at some large subset of paths instead of the entire space
    #Obviously this isn't great in the worst case, but it is good in the average case
    # if len(lst) > 120:
    #     lst = lst[:120]
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

# In[12]:

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

# In[13]:

def harmMatrices(timeValues, destinations, distMatrix):
    #distMatrix = distanceMatrix(destinations)
    allPaths = pathList(destinations)
    #allPaths = transform_path_list(allPaths)
    optPath = optimalPath(timeValues,allPaths,distMatrix)
    shortPath = shortestPath(allPaths,distMatrix)
    shortPath = allPaths[shortPath]
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
    output.append(subOptCosts[0].tolist())
    for i in range(len(timeValues)):
        if i > 0:
            payments = subOptCosts[0]-subOptCosts[i]
            payments[i] = 0
            output.append(payments.tolist())

    return output, subOptPaths, subOptCosts

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

carCost = 50
#Estimated car value of time to be equivalent to 15K/year earner
def random_time_values(incomes, n, p, carCost=carCost):
    timeValues = np.random.choice(incomes, n, p=p)
    timeValues = np.append(carCost, timeValues)
    timeValues *= (1/2.0)
    return(timeValues)


def gen_time_values():
    return random_time_values(uberIncomes, 5, uberIncomesDist)

# In[14]:


def get_info_from_inputs(num_locations=5, locationFile='locations.txt'):
    inp_locations = readInputLocations(locationFile)
    processed_array = randomLocations(inp_locations, num_locations)
    response = sendRequest(processed_array)
    addresses = response["origin_addresses"]
    durMatrix = getDurationMatrix(response)
    distMatrix = getDistanceMatrix(response)
    return addresses, processed_array, durMatrix, distMatrix

# addresses, lat_longs, durMatrix, distMatrix = get_info_from_inputs()

# lat_longs = processed_array
# # In[16]:

# #rerandomize timevalues
# timeValues = gen_time_values()
# # timeValues


# # In[17]:

# timeValues = gen_time_values()
# destinations = [(dest[0], dest[1], i) for i, dest in enumerate(processed_array)]
# output, paths, costs = harmMatrices(timeValues, destinations, durMatrix)

# # # In[18]:

# destinations


# In[19]:




# In[20]:

# costs


# In[21]:

# paths

#path 0 is shortest
#path 1 is optimal