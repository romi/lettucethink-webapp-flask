"""
    main.py

    Copyright (C) 2017 Sony Computer Science Laboratories
    Authors: David Colliaux & Peter Hanappe

    main.py is part of LettuceThink Web Interface.

    LettuceThink is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from flask import Flask, render_template, Response, request, redirect, jsonify, make_response, send_file
from lettucethink import dummy
import requests
import datetime
import time
import json
import io
import imageio
import CNCWorker

imgdir = "/tmp"

app = Flask(__name__)
worker = CNCWorker.CNCWorker()

camera = dummy.Camera("topcam.jpg")


def getFarmId():
    return "valldaura"

def indexPage():
    return render_template('button.html')

def weedingPage():
    location = {"bed": 0, "zone": 0}
    return render_template('weeding.html', location=location)

def homingPage():
    location = {"bed": 0, "zone": 0}
    return render_template('homing.html', location=location)

    
@app.route('/')
def index():
    return indexPage()


@app.route('/cnc_status')
def cnc_status():
    global worker
    s, p = worker.getStatus()
    return jsonify(status=s, progress=p)

    
@app.route('/hoe_all')
def hoeAll():
    global worker
    worker.nextRun(0, 0, "boustrophedon")
    return weedingPage()

   
@app.route('/homing')
def homing():
    worker.homing()
    return homingPage()


@app.route('/cancel')
def cancel():
    worker.cancel()
    return indexPage()


@app.route('/toolup')
def toolup():
    worker.changeZ(10)
    return "ok"


@app.route('/tooldown')
def tooldown():
    worker.changeZ(-10)
    return "ok"


@app.route('/topcam.jpg')
def topcam():
#    img = camera.grab()
#    return Response(img, mimetype="image/jpeg")
#    
#    image = camera.grab()
#    byte_array = io.BytesIO()
#    image.save(byte_array, format='JPG')
#    byte_array = byte_array.getvalue()
#    response = make_response(byte_array)
#    response.headers.set('Content-Type', 'image/jpeg')
#    return response
#
    return send_file("topcam.jpg", mimetype='image/jpg')

@app.route('/config.html')
def configPage():
    return render_template('config.html')


@app.route('/movedown')
def movedown():
    worker.moveZ(-10)
    return jsonify(status="ok")


@app.route('/moveup')
def moveup():
    worker.moveZ(10)
    return jsonify(status="ok")


@app.route('/stopmoving')
def stopmoving():
    worker.moveZ(0)
    return jsonify(status="ok")


@app.route('/setz0')
def setz0():
    worker.setZ0()
    return jsonify(status="ok")


@app.route('/setz1')
def setz1():
    worker.setZ1()
    return jsonify(status="ok")


if __name__=='__main__':
    app.run(host = '0.0.0.0', debug = False, threaded = False)
