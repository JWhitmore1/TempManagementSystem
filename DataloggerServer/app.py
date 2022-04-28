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
    # (possibly from incomplete serial transmission making server crash)
    try:
        arduino_json = json.loads(data)
    except:
        return redirect("/")
    arduino_json['data_date_time'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # uncomment to fix arduino clock module time inacuracies by making sure the time is right

    return arduino_json
