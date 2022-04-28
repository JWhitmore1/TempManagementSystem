from flask import Flask, redirect
import serial
import json
import datetime

app = Flask(__name__)

# running on raspberry pi as API with datalogger data
@app.route('/')
def index():
    # get serial JSON from arduino
    ser = serial.Serial('/dev/ttyACM0', 9600)
    data = ser.readline().decode("utf-8")
    # occasionally errors were thrown when decoding JSON 
    # (from incomplete serial transmission) and server would crash
    try:
        arduino_json = json.loads(data)
    except:
        return redirect("/")
    # fix arduino clock module time inacuracies by double checking the time is right
    arduino_json['data_date_time'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    return arduino_json
