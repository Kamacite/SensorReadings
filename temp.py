import os
from flask import Flask, render_template
from flask_moment import Moment

import requests
import re
import urllib3
import json

app = Flask(__name__)
moment = Moment(app)

def c_to_f(temp):
    return temp*(9.0/5.0) + 32.0

def get_sensor_reading(url):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        r = requests.get(url, auth=('user', 'password'), verify=False, timeout=3)
        if(r.status_code == 200):
            data = float(re.search('(?<=<double-val>)[-0123456789.]*', r.text).group(0))
        else:
            data = -1000.0
    except:
        data = -1000.0
    return data

def format_sensors(sensors):
    for sensor in sensors:
        reading = get_sensor_reading(sensor['url'])
        if reading == -1000.0:
            sensor['data'] = -1000.0
            sensor['str_data']= "No Data"
        elif sensor['type'] == "Temperature":
            sensor['data'] = round(c_to_f(reading), 2)
            sensor['str_data'] = str(sensor['data']) + '\xb0F'
        elif sensor['type'] == "Humidity":
            sensor['data'] = round(reading, 2)
            sensor['str_data'] = str(sensor['data']) + "%"
        elif sensor['type'] == "Dew Point":
            sensor['data'] = round(c_to_f(reading), 2)
            sensor['str_data'] = str(sensor['data']) + '\xb0F'
        else:
            pass
    return sensors

@app.route('/')
@app.route('/<int:refresh>')
def index(refresh=60):
    f = open("./sensors.json", "r")
    sensors_data = json.loads(f.read())
    f.close()
    site1_sensors = sensors_data['site1_sensors']
    site1_sensors = format_sensors(site1_sensors)
    site2_sensors = sensors_data['site2_sensors']
    site2_sensors = format_sensors(site2_sensors)

    return render_template('index.jinja',refresh=refresh,site1_sensors=site1_sensors, site2_sensors=site2_sensors)
	
if __name__ == "__main__":
	app.run()


