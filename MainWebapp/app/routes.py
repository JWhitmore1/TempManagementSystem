from crypt import methods
from app import app
from app.db import close_db, get_db
from flask import redirect, render_template, request
import requests
import math

# Function to calculate apparent temperature based on arguments: temp (t) and humidity (h)
def calculateTemp(t, h):
    p = (h/100)*6.105*math.exp((17.27*t)/(237.7+t))
    aptTemp = round(t + (0.33 * p) - 4, 1)
    return aptTemp

# function to get weather data from the BOM API
def requestBOMWeather():
    r = requests.get('http://reg.bom.gov.au/fwo/IDQ60901/IDQ60901.94576.json')
    weather_json = r.json()
    weather_data = weather_json['observations']['data']
    return weather_data

# function to request the internal weather data from the datalogger server (arduino and raspberry pi)
def requestIntWeather():
    r = requests.get('http://118.208.156.84:5000/')
    weather_data = r.json()
    # print(weather_data)
    return weather_data

# function to get the current threshold from the database
def getThreshold():
    db = get_db()
    result = db.execute('SELECT thresholdMax FROM Thresholds WHERE id = 1').fetchone()[0]
    close_db()
    return result

# function to update the external weather database with the newest data 
def updateExtWeather():
    weather_data = requestBOMWeather()
    db = get_db()
    for weather in weather_data:
        data_date_time = weather['local_date_time_full']
        result = db.execute('SELECT * FROM ExternalWeather WHERE date_time_full = ?', (data_date_time,))
        allresults = result.fetchall()
        # checks if the data is already in database, if it isnt, adds it
        if allresults == []:
            db.execute('INSERT INTO ExternalWeather (data_date_time, date_time_full, apparent_t, true_t, rel_hum)'
                       'VALUES (?, ?, ?, ?, ?);', (weather['local_date_time'], weather['local_date_time_full'], weather['apparent_t'], weather['air_temp'], weather['rel_hum']))
            db.commit()
    close_db()

# function to update the internal weather database with newest data
def updateIntWeather():
    weather = requestIntWeather()
    db = get_db()
    data_date_time = weather['data_date_time']
    result = db.execute('SELECT * FROM InternalWeather WHERE data_date_time = ?', (data_date_time,))
    allresults = result.fetchall()
    # checking if data is present already, adding it if not
    if allresults == []:
        db.execute('INSERT INTO InternalWeather (data_date_time, true_t, rel_hum)'
                    'VALUES (?, ?, ?);', (weather['data_date_time'], weather['true_t'], weather['humidity']))
        db.commit()
    close_db()

@app.route('/')
def index():
    # index is empty for now so redirects to the weather page
    return redirect("/weather")

# main weather dashboard 
@app.route('/weather')
def weather():

    # calling previously defined functions to update the weather data
    updateIntWeather()
    updateExtWeather()
    # getting the weather data for use on page
    int_data = requestIntWeather()
    bom_data = requestBOMWeather()[0]
    
    # checking if temperature is above safety threshold
    apIntTemp = calculateTemp(int_data['true_t'], int_data['humidity'])
    if apIntTemp > getThreshold():
        warning = True
    else:
        warning = False

    # creating list of data for display on website
    weather_data = [apIntTemp, int_data['true_t'], int_data['humidity'], 
                    bom_data['apparent_t'], bom_data['air_temp'], bom_data['rel_hum']]
    
    # returns the html page along with all needed variables
    return render_template('temps.html', weather_data=weather_data, warning=warning, threshold=getThreshold())

# page for the historical data and graphs
@app.route('/historical')
def historical():
    
    updateExtWeather()

    # get data in the correct order from the last 3 days - for graph
    db = get_db()
    all_temps_query = db.execute('SELECT * FROM (SELECT apparent_t, data_date_time, date_time_full FROM ExternalWeather ORDER BY date_time_full DESC LIMIT 144) ORDER BY date_time_full ASC')
    all_temps = [(row['data_date_time'], row['apparent_t']) for row in all_temps_query]
    close_db()

    return render_template('historical.html', all_temps=all_temps)

# settings page (currently only for updating threshold)
@app.route('/settings')
def settings():

    # get current threshold value to display in the input
    threshold = getThreshold()

    return render_template('settings.html', curThreshold = threshold)

# on settingds form submit redirct here with value in threshold input
@app.route('/updateThreshold', methods=["GET", "POST"])
def updateThreshold():

    # update threshold in db
    threshold = request.form.get('threshold')
    db = get_db()
    db.execute('UPDATE Thresholds SET thresholdMax = ? WHERE id = 1;', (threshold,))
    db.commit()
    close_db()

    # redirect to dashboard
    return redirect('/weather')