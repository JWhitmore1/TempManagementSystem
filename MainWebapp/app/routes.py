from crypt import methods
from app import app
from app.db import close_db, get_db
from flask import redirect, render_template, request
from app.functions import *

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