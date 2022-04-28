import requests
import math
from app.db import close_db, get_db

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
    # ocasionally json decode throws errors unexpectedly, still don't know why
    try:
        weather_data = r.json()
    except:
        print("json decode error")
        weather_data = []
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