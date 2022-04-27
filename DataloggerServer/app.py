from flask import Flask, redirect
import serial
import json

app = Flask(__name__)

@app.route('/')
def index():
    ser = serial.Serial('/dev/cu.usbmodem11301', 9600)
    data = ser.readline().decode("utf-8")
    try:
        arduino_json = json.loads(data)
    except:
        return redirect("/")
    return arduino_json
