#!/usr/bin/env python

from flask import Flask, render_template, redirect, url_for, send_file
import psutil
import datetime
import plant_pi
import os
import _thread

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

pc = plant_pi.PlantController()

# Set up title, headers, etc for home page
def template(title = "Plant Town", text = "This is me:"):
    now = datetime.datetime.now()
    timeString = now
    templateDate = {
        'title' : title,
        'time' : timeString,
        'text' : text
        }
    return templateDate

# Set home page
@app.route("/")
def hello():
    templateData = template()
    return render_template('main.html', **templateData)

# Read moisture sensor
@app.route("/sensor1")
def action():
    status = pc.read_moisture(1)
    message = ""
    percent_dry = int((status-0.55) / 0.3 * 100)
    message = "I'm " + str(percent_dry) + "% dry."

    if (status > 0.7):
        message += " Too dry help me."
    else:
        message += " I'm a happy plant."

    templateData = template(text = message)
    return render_template('main.html', **templateData)

# Read light sensor
@app.route("/sensor2")
def action3():
    status = pc.read_lux()
    message = "Light in lux: " + str(status)

    templateData = template(text = message)
    return render_template('main.html', **templateData)

# Water the plant once (run pump for x secs)
@app.route("/water")
def action2():
    pc.run_pump(5)
    templateData = template(text = "Watered Once")
    return render_template('main.html', **templateData)
    
# Rotate to brightest position
@app.route("/lightscan")
def light_scan():
    l, p = pc.run_servo_scan()
    message = "Plant at position " + str(p) + " receiving " + str(l) + " sun power"
    templateData = template(text = message)
    return render_template('main.html', **templateData)
    
# Rotate once
@app.route("/rotate")
def rotate_once():
    p = pc.rotate_plant()
    message = "Plant at position " + str(p)
    templateData = template(text = message)
    return render_template('main.html', **templateData)
    
# Path for camera image
@app.route("/image")
def show_plant():
    path = pc.photo_path
    return send_file(path)
    
# Take photo with camera
@app.route("/photo")
def take_pic():
    pc.take_photo()
    templateData = template(text = "Photo Taken")
    return render_template('main.html', **templateData)

# Run auto-loop in a new thread
@app.route("/loop")
def run_loop():
    if pc.run_loop:
        templateData = template(text = "Already Looping")
    else:
        pc.run_loop = True
        _thread.start_new_thread(pc.loop, (60,))
        templateData = template(text = "Running Loop")
    return render_template('main.html', **templateData)
    
# End auto-loop
@app.route("/endloop")
def kill_loop():
    pc.run_loop = False
    templateData = template(text = "Ending Loop")
    return render_template('main.html', **templateData)

# Path for graph image
@app.route("/graph_image")
def show_data():
    path = pc.graph_path

    return send_file(path)

# Update graphs by reloading json data
@app.route("/update_graph")
def update_graph():
    pc.save_data_to_graph()
    os.remove('records/tmp.json')
    templateData = template(text = "Graph Updated")
    return render_template('main.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
