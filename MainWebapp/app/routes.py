from crypt import methods
from app import app
from app.db import close_db, get_db
from flask import redirect, render_template, request
import requests
import math

def calculateTemp(t, h):
    p = (h/100)*6.105*math.exp((17.27*t)/(237.7+t))
    aptTemp = round(t + (0.33 * p) - 4, 1)
    return aptTemp

def requestBOMWeather():
    r = requests.get('http://reg.bom.gov.au/fwo/IDQ60901/IDQ60901.94576.json')
    weather_json = r.json()
    weather_data = weather_json['observations']['data']
    return weather_data

def requestIntWeather():
    r = requests.get('http://118.208.156.84:5000/')
    weather_data = r.json()
    # print(weather_data)
    return weather_data

def getThreshold():
    db = get_db()
    result = db.execute('SELECT thresholdMax FROM Thresholds WHERE id = 1').fetchone()[0]
    close_db()
    return result

def updateExtWeather():
    weather_data = requestBOMWeather()
    db = get_db()
    for weather in weather_data:
        data_date_time = weather['local_date_time_full']
        result = db.execute('SELECT * FROM ExternalWeather WHERE date_time_full = ?', (data_date_time,))
        allresults = result.fetchall()
        if allresults == []:
            # print("Adding a row")
            db.execute('INSERT INTO ExternalWeather (data_date_time, date_time_full, apparent_t, true_t, rel_hum)'
                       'VALUES (?, ?, ?, ?, ?);', (weather['local_date_time'], weather['local_date_time_full'], weather['apparent_t'], weather['air_temp'], weather['rel_hum']))
            db.commit()
    close_db()

def updateIntWeather():
    weather = requestIntWeather()
    db = get_db()
    data_date_time = weather['data_date_time']
    # print(weather['data_date_time'], weather['true_t'], weather['humidity'])
    result = db.execute('SELECT * FROM InternalWeather WHERE data_date_time = ?', (data_date_time,))
    allresults = result.fetchall()
    if allresults == []:
        # print("Adding a row")
        db.execute('INSERT INTO InternalWeather (data_date_time, true_t, rel_hum)'
                    'VALUES (?, ?, ?);', (weather['data_date_time'], weather['true_t'], weather['humidity']))
        db.commit()
    close_db()

@app.route('/')
def index():
    return redirect("/weather")

@app.route('/weather')
def weather():

    updateIntWeather()
    updateExtWeather()
    int_data = requestIntWeather()
    bom_data = requestBOMWeather()[0]
    
    apIntTemp = calculateTemp(int_data['true_t'], int_data['humidity'])
    if apIntTemp > getThreshold():
        warning = True
    else:
        warning = False

    weather_data = []
    weather_data = [apIntTemp, int_data['true_t'], int_data['humidity'], 
                    bom_data['apparent_t'], bom_data['air_temp'], bom_data['rel_hum']]
    
    return render_template('temps.html', weather_data=weather_data, warning=warning, threshold=getThreshold())

@app.route('/historical')
def historical():
    
    updateExtWeather()

    db = get_db()
    all_temps_query = db.execute('SELECT * FROM (SELECT apparent_t, data_date_time, date_time_full FROM ExternalWeather ORDER BY date_time_full DESC LIMIT 144) ORDER BY date_time_full ASC')
    all_temps = [(row['data_date_time'], row['apparent_t']) for row in all_temps_query]
    close_db()

    return render_template('historical.html', all_temps=all_temps)

@app.route('/settings')
def settings():

    # get current threshold value for the input value
    threshold = getThreshold()

    return render_template('settings.html', curThreshold = threshold)

@app.route('/updateThreshold', methods=["GET", "POST"])
def updateThreshold():

    # update threshold in db
    threshold = request.form.get('threshold')
    db = get_db()
    db.execute('UPDATE Thresholds SET thresholdMax = ? WHERE id = 1;', (threshold,))
    db.commit()
    close_db()

    return redirect('/weather')