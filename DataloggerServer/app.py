from flask import Flask, redirect
import serial
import json
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    # running on raspberry pi
    ser = serial.Serial('/dev/ttyACM0', 9600)
    data = ser.readline().decode("utf-8")
    try:
        arduino_json = json.loads(data)
        arduino_json['data_date_time'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    except:
        return redirect("/")
    return arduino_json
