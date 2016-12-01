import os, time
from flask import Flask, Response, render_template, jsonify
from geojson import Point, Feature, FeatureCollection
from .distReq import randomLocations, readInputLocations, getDurationMatrix, getDistanceMatrix# uncomment this when using in another file



app = Flask(__name__)
app.debug = True

ACCESS_KEY = os.environ.get('MAPBOX_ACCESSKEY')

@app.route('/')
def index():
    return render_template('index.html', ACCESS_KEY=ACCESS_KEY)

@app.route('/origin')
def processOrigin():
    point = Point((-87.9073, 41.9742))
    feature = Feature(geometry=point ,properties={'marker-color': '#3ca0d3','marker-size': 'large','marker-symbol': 'airport'})
    feature_collection = FeatureCollection([feature])
    return jsonify(result=feature_collection)

@app.route('/dest')
def processDestinations():
    destinationFeatureArray = []
    numRiders = 5
    locationFile = "locations.txt" # stores all the lat/longs on different lines
    processedArray = randomLocations(readInputLocations(locationFile), numRiders)
    # response = sendRequest(processedArray)
    # addresses = response["origin_addresses"] # list of length numLocations of the addresses
    for i in range(1, len(processedArray)):
        point = Point((processedArray[i][1],processedArray[i][0]))
        feature =  Feature(geometry=point ,properties= {'marker-color': '#228B22','marker-size': 'medium','marker-symbol': str(i)})
        destinationFeatureArray.append(feature)
    # durMatrix = getDurationMatrix(response)
    # distMatrix = getDistanceMatrix(response)
    feature_collection = FeatureCollection(destinationFeatureArray)
    return jsonify(result=feature_collection)


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


if __name__ == '__main__':
    app.run(debug = True)
