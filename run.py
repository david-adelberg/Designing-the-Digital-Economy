import os, time
from flask import Flask, Response, render_template, jsonify, session, request, redirect, url_for
from geojson import Point, Feature, FeatureCollection
from distReq import randomLocations, readInputLocations, getDurationMatrix, getDistanceMatrix, sendRequest# uncomment this when using in another file
from findPath import  harmMatrices, random_time_values, indivCostMat
from mapbox import Directions
import numpy as np
from flask_bootstrap import Bootstrap

# import things
from flask_table import Table, Col

app = Flask(__name__)
Bootstrap(app)
app.debug = True
app.secret_key = 'correctHorseBatteryStaple'
app.config['SESSION_TYPE'] = 'filesystem'


destinationFeatureArray = []
response = [];
distMatrix = []
durMatrix = []
addreses = []
paths = []
costs = []
output = []
originFeature = []

uberIncomesRaw = [25.0, 50.0, 85.0, 150.0, 300.0, 600.0]
uberIncomesDistRaw = [8.0,23.0,18.0,27.0,9.0, 2.0]
# Note that this doesn't sum to 100, because about 20% of uber drivers
# declined to share their income with the surveyors

uberIncomes = uberIncomesRaw/(np.ones(len(uberIncomesRaw)))
# Note that these numbers are not normalized in any way
# In production, these numbers should be in units of $/minute

uberIncomesDist = uberIncomesDistRaw/np.sum(uberIncomesDistRaw)


ACCESS_KEY = os.environ.get('MAPBOX_ACCESSKEY')
service = Directions(ACCESS_KEY)
@app.route('/')
def index():
    return render_template('index.html', ACCESS_KEY=ACCESS_KEY)



# Declare your table
class RiderTable(Table):
    name = Col('Rider Name')
    valuation = Col('Time Valuation ($/hr)')
    duration = Col('Trip Duration (minutes)')
    payment = Col('Payment ($)')

class RiderComp(Table):
    name = Col('Rider Name')
    comp = Col('Compensation for other Rider')

@app.route('/stats')
def harm():
    payments = session.get('payments', None)
    timeValuation = session.get('timeValuation', None)
    durMatrix = session.get('durMatrix', None)
    num_riders = len(payments[0])-1 # 1 cost per rider

    # 1 table that has just the riders names, time valuation, time in car, payment

    # 1 table that has riders names and payments to other riders
    paths = session.get('paths', None)
    socialPath = paths[0]
    optPath = paths[1]

    onesList = [1] * (num_riders+1)
    soc_durations = indivCostMat(onesList, socialPath, durMatrix)

    soc_riders = []
    soc_cost = 0
    soc_uber_cost = str(round(timeValuation[0] * soc_durations[0] /3600, 2)) # $
    soc_ride_time = str(round(soc_durations[0]/60, 2)) #mins
    for i in range(num_riders):
        soc_cost += np.sum(payments[i+1])/3600

    for i in range(num_riders):
        rider = dict(name=chr(65+i), valuation=str(timeValuation[i+1]),duration=str(round(soc_durations[i+1]/60,2)), payment=str(round(soc_cost/num_riders,2))) #3600 to convert to per hour
        soc_riders.append(rider)

    opt_durations = indivCostMat(onesList, optPath, durMatrix)
    opt_riders = []
    opt_uber_cost = str(round(timeValuation[0] * opt_durations[0] /3600, 2))
    opt_ride_time = str(round(opt_durations[0]/60,2)) #mins
    for i in range(num_riders):
        rider = dict(name=chr(65+i), valuation=str(timeValuation[i+1]),duration=str(round(opt_durations[i+1]/60,2)), payment=str(round(np.sum(payments[i+1])/3600,2))) #3600 to convert to per hour
        opt_riders.append(rider)

    # Populate the table
    rider_table = RiderTable(opt_riders)
    rider2_table = RiderTable(soc_riders)

    return render_template('harm.html', opt_table=rider_table, soc_table=rider2_table, soc_uber_cost = soc_uber_cost, opt_uber_cost=opt_uber_cost, soc_ride_time=soc_ride_time, opt_ride_time=opt_ride_time)

@app.route('/origin')
def processOrigin():
    point = Point((-87.9073, 41.9742))
    originFeature = Feature(geometry=point ,properties={'marker-color': '#3ca0d3','marker-size': 'large','marker-symbol': 'airport'})
    feature_collection = FeatureCollection([originFeature])
    session['originFeature'] = originFeature
    return jsonify(result=feature_collection)

@app.route('/dest')
def processDestinations():
    numRiders = session.get('numRiders', 5)
    print numRiders
    locationFile = "locations.txt" # stores all the lat/longs on different lines
    processedArray = randomLocations(readInputLocations(locationFile), numRiders)
    destinationFeatureArray = []
    for i in range(1, len(processedArray)):
        point = Point((processedArray[i][1],processedArray[i][0]))
        feature =  Feature(geometry=point ,properties= {'marker-color': '#228B22','marker-size': 'medium','marker-symbol': chr(96+i)})
        destinationFeatureArray.append(feature)
    session['destinationFeatureArray']= destinationFeatureArray
    feature_collection = FeatureCollection(destinationFeatureArray)
    response = sendRequest(processedArray,[])
    session['addresses'] = addresses = response["origin_addresses"] # list of length numLocations of the addresses
    session['durMatrix'] = durMatrix = getDurationMatrix(response)
    session['distMatrix'] = distMatrix = getDistanceMatrix(response)

    timeValues = random_time_values(uberIncomes, numRiders, uberIncomesDist)
    session['timeValuation'] = timeValues.tolist()

    destinations = [(dest[0], dest[1], i) for i, dest in enumerate(processedArray)]
    output, paths, costs = harmMatrices(timeValues, destinations, durMatrix)
    session['paths']=paths
    print output
    session['payments']= output
    return jsonify(result=feature_collection)

@app.route('/social')
def socialRoute():
    paths = session.get('paths', None)
    originFeature = session.get('originFeature', None)
    destinationFeatureArray = session.get('destinationFeatureArray', None)
    socialPath = paths[0]
    featureDict = []
    featureDict.append(originFeature);
    for i in range(1,len(socialPath)):
        featureDict.append(destinationFeatureArray[socialPath[i][2]-1])
    response2 = service.directions(featureDict, 'mapbox.driving')
    print response2
    responseJson = response2.geojson()
    # responseJson['style'] = {"style":{ "fill":"red", "stroke-width":"3", "fill-opacity":0.6}}
    # responseJson['features'][0]['properties']['fill']=  '#228B22'
    responseJson['features'][0]['properties']['title']=  'Social Optimal Path'
    responseJson['features'][0]['properties']['stroke']=  '#000080' # lime
    responseJson['features'][0]['properties']['stroke-opacity']=  '0.7'
    responseJson['features'][0]['properties']['stroke-width']=  '6'

    return jsonify(result=responseJson)


@app.route('/opt')
def optRoute():
    paths = session.get('paths', None)
    originFeature = session.get('originFeature', None)
    destinationFeatureArray = session.get('destinationFeatureArray', None)
    optPath = paths[1]
    featureDict = []
    featureDict.append(originFeature);
    for i in range(1,len(optPath)):
        featureDict.append(destinationFeatureArray[optPath[i][2]-1])
    response2 = service.directions(featureDict, 'mapbox.driving')
    # print response2
    responseJson = response2.geojson()
    responseJson['features'][0]['properties']['title']=  'Utility Optimal Path'
    responseJson['features'][0]['properties']['stroke']=  '#00FF00' # lime
    responseJson['features'][0]['properties']['stroke-opacity']=  '0.7'
    responseJson['features'][0]['properties']['stroke-width']=  '4'
    return jsonify(result=responseJson)


@app.route('/process')
def long_running_process():
      def generate():
        # time.sleep(10)
        yield 'data: Chicago O\'Hare Airport marker placed \n\n'
      return Response(generate(), mimetype='text/event-stream')

@app.route('/process2')
def long_running_process2():
      def generate2():
        yield 'data: Destination markers placed \n\n'
      return Response(generate2(), mimetype='text/event-stream')

@app.route('/process3')
def long_running_process3():
      def generate3():
        yield 'data: Social Path \n\n'
      return Response(generate3(), mimetype='text/event-stream')

@app.route('/process4')
def long_running_process4():
      def generate4():
        yield 'data: Optimal Path \n\n'
      return Response(generate4(), mimetype='text/event-stream')

@app.route('/riders', methods=['POST'])
def my_form_post():
    if request.form['numRiders'].isdigit() and int(request.form['numRiders']) < 10 and int(request.form['numRiders']) > 0:
        session["numRiders"] = int(request.form['numRiders'])
    return redirect(url_for('index'))



if __name__ == "__main__":
    app.run()
