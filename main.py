"""
    main.py

    Copyright (C) 2017 David Colliaux & Peter Hanappe, Sony Computer
    Science Laboratories

    main.py is part of LettuceThink.

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
from flask import Flask, render_template, Response, request, redirect, jsonify
import requests
import datetime
import time
import json
import CNCWorker

imgdir = "/tmp"
topcamUrl = "http://lettucethink-topcam.local:10000/image.jpg"
tagsUrl = "http://lettucethink-topcam.local:10000/tags.json"
captureUrl = "http://lettucethink-topcam.local:10000/capture"

app = Flask(__name__)
worker = CNCWorker.CNCWorker()

names = ["I1", "E1", "E3"]

beds = {
    "I1": [
        ["I1", 1, "r-man-1", "Radis - manuel (1)", "skip", 0, "#cdde87ff"],
        ["I1", 2, "r-man-2", "Radis - manuel (2)", "skip", 0, "#cdde87ff"],
        ["I1", 3, "r-man-3", "Radis - manuel (3)", "skip", 0, "#cdde87ff"],
        ["I1", 4, "r-x-1", "Radis - pas de passage (1)", "skip", 0, "#ffffff"],
        ["I1", 5, "r-x-2", "Radis - pas de passage (2)", "skip", 0, "#ffffff"],
        ["I1", 6, "r-x-3", "Radis - pas de passage (3)", "skip", 0, "#ffffff"],
        ["I1", 7, "r-sel-1", "Radis - désherbage sélectif (1)", "hoe_weeds", 0, "#abc837ff"],
        ["I1", 8, "r-sel-2", "Radis - désherbage sélectif (2)", "hoe_weeds", 0, "#abc837ff"],
        ["I1", 9, "r-sel-3", "Radis - désherbage sélectif (3)", "hoe_weeds", 0, "#abc837ff"],
        ["I1", 10, "r-comp-1", "Radis - désherbage complet (1)", "hoe_inbetween", 0, "#89a02cff"],
        ["I1", 11, "r-comp-2", "Radis - désherbage complet (2)", "hoe_inbetween", 0, "#89a02cff"],
        ["I1", 12, "r-comp-3", "Radis - désherbage complet (3)", "hoe_inbetween", 0, "#89a02cff"],
        ["I1", 13, "f-0x-1", "Fréquence - pas de passage (1)", "skip", 0, "#ffffff"],
        ["I1", 14, "f-0x-2", "Fréquence - pas de passage (2)", "skip", 0, "#ffffff"],
        ["I1", 15, "f-0x-3", "Fréquence - pas de passage (3)", "skip", 0, "#ffffff"],
        ["I1", 16, "f-05x-1", "Fréquence - 1x / 2 sem. (1)", "hoe_all", 14, "#c4eaeeff"],
        ["I1", 17, "f-05x-2", "Fréquence - 1x / 2 sem. (2)", "hoe_all", 14, "#c4eaeeff"],
        ["I1", 18, "f-05x-3", "Fréquence - 1x / 2 sem. (3)", "hoe_all", 14, "#c4eaeeff"],
        ["I1", 19, "f-1x-1", "Fréquence - 1x / sem. (1)", "hoe_all", 7, "#74ced8ff"],
        ["I1", 20, "f-1x-2", "Fréquence - 1x / sem. (2)", "hoe_all", 7, "#74ced8ff"],
        ["I1", 21, "f-1x-3", "Fréquence - 1x / sem. (3)", "hoe_all", 7, "#74ced8ff"],
        ["I1", 22, "f-2x-1", "Fréquence - 2x / sem. (1)", "hoe_all", 3.5, "#46bccbff"],
        ["I1", 23, "f-2x-2", "Fréquence - 2x / sem. (2)", "hoe_all", 3.5, "#46bccbff"],
        ["I1", 24, "f-2x-3", "Fréquence - 2x / sem. (3)", "hoe_all", 3.5, "#46bccbff"],
        ["I1", 25, "g-ax-1", "Germination - terre argileuse - pas de passage (1)", "skip", 0, "#b4471cff"],
        ["I1", 26, "g-ax-2", "Germination - terre argileuse - pas de passage (2)", "skip", 0, "#b4471cff"],
        ["I1", 27, "g-ax-3", "Germination - terre argileuse - pas de passage (3)", "skip", 0, "#b4471cff"],
        ["I1", 28, "g-ap-1", "Germination - terre argileuse - passage (1)", "hoe_all", 0, "#b4471cff"],
        ["I1", 29, "g-ap-2", "Germination - terre argileuse - passage (2)", "hoe_all", 0, "#b4471cff"],
        ["I1", 30, "g-ap-3", "Germination - terre argileuse - passage (3)", "hoe_all", 0, "#b4471cff"],
        ["I1", 31, "g-sx-1", "Germination - terre sableuse - pas de passage (1)", "skip", 0, "#ffbf55ff"],
        ["I1", 32, "g-sx-2", "Germination - terre sableuse - pas de passage (2)", "skip", 0, "#ffbf55ff"],
        ["I1", 33, "g-sx-3", "Germination - terre sableuse - pas de passage (3)", "skip", 0, "#ffbf55ff"],
        ["I1", 34, "g-sp-1", "Germination - terre sableuse - passage (1)", "hoe_all", 0, "#ffbf55ff"],
        ["I1", 35, "g-sp-2", "Germination - terre sableuse - passage (2)", "hoe_all", 0, "#ffbf55ff"],
        ["I1", 36, "g-sp-3", "Germination - terre sableuse - passage (3)", "hoe_all", 0, "#ffbf55ff"]],
    "E1": [
        ["E1", 1, "r-man-1", "Radis - manuel (1)", "skip", 0, "#cdde87ff"],
        ["E1", 2, "r-man-2", "Radis - manuel (2)", "skip", 0, "#cdde87ff"],
        ["E1", 3, "r-man-3", "Radis - manuel (3)", "skip", 0, "#cdde87ff"],
        ["E1", 4, "r-x-1", "Radis - pas de passage (1)", "skip", 0, "#ffffff"],
        ["E1", 5, "r-x-2", "Radis - pas de passage (2)", "skip", 0, "#ffffff"],
        ["E1", 6, "r-x-3", "Radis - pas de passage (3)", "skip", 0, "#ffffff"],
        ["E1", 7, "r-sel-1", "Radis - désherbage sélectif (1)", "hoe_weeds", 0, "#abc837ff"],
        ["E1", 8, "r-sel-2", "Radis - désherbage sélectif (2)", "hoe_weeds", 0, "#abc837ff"],
        ["E1", 9, "r-comp-1", "Radis - désherbage complet (1)", "hoe_inbetween", 0, "#89a02cff"],
        ["E1", 10, "r-comp-2", "Radis - désherbage complet (2)", "hoe_inbetween", 0, "#89a02cff"],
        ["E1", 11, "r-comp-3", "Radis - désherbage complet (3)", "hoe_inbetween", 0, "#89a02cff"],
        ["E1", 12, "f-0x-1", "Fréquence - pas de passage (1)", "skip", 0, "#ffffff"],
        ["E1", 13, "f-0x-2", "Fréquence - pas de passage (2)", "skip", 0, "#ffffff"],
        ["E1", 14, "f-0x-3", "Fréquence - pas de passage (3)", "skip", 0, "#ffffff"],
        ["E1", 15, "f-05x-1", "Fréquence - 1x / 2 sem. (1)", "hoe_all", 14, "#c4eaeeff"],
        ["E1", 16, "f-05x-2", "Fréquence - 1x / 2 sem. (2)", "hoe_all", 14, "#c4eaeeff"],
        ["E1", 17, "f-05x-3", "Fréquence - 1x / 2 sem. (3)", "hoe_all", 14, "#c4eaeeff"],
        ["E1", 18, "f-1x-1", "Fréquence - 1x / sem. (1)", "hoe_all", 7, "#74ced8ff"],
        ["E1", 19, "f-1x-2", "Fréquence - 1x / sem. (2)", "hoe_all", 7, "#74ced8ff"],
        ["E1", 20, "f-1x-3", "Fréquence - 1x / sem. (3)", "hoe_all", 7, "#74ced8ff"],
        ["E1", 21, "f-2x-1", "Fréquence - 2x / sem. (1)", "hoe_all", 3.5, "#46bccbff"],
        ["E1", 22, "f-2x-2", "Fréquence - 2x / sem. (2)", "hoe_all", 3.5, "#46bccbff"],
        ["E1", 23, "f-2x-3", "Fréquence - 2x / sem. (3)", "hoe_all", 3.5, "#46bccbff"]],
    "E3": [
        ["E3", 1, "r-man-1", "Radis - manuel (1)", "skip", 0, "#cdde87ff"],
        ["E3", 2, "r-man-2", "Radis - manuel (2)", "skip", 0, "#cdde87ff"],
        ["E3", 3, "r-man-3", "Radis - manuel (3)", "skip", 0, "#cdde87ff"],
        ["E3", 4, "r-x-1", "Radis - pas de passage (1)", "skip", 0, "#ffffff"],
        ["E3", 5, "r-x-2", "Radis - pas de passage (2)", "skip", 0, "#ffffff"],
        ["E3", 6, "r-x-3", "Radis - pas de passage (3)", "skip", 0, "#ffffff"],
        ["E3", 7, "r-sel-1", "Radis - désherbage sélectif (1)", "hoe_weeds", 0, "#abc837ff"],
        ["E3", 8, "r-sel-2", "Radis - désherbage sélectif (2)", "hoe_weeds", 0, "#abc837ff"],
        ["E3", 9, "r-comp-1", "Radis - désherbage complet (1)", "hoe_inbetween", 0, "#89a02cff"],
        ["E3", 10, "r-comp-2", "Radis - désherbage complet (2)", "hoe_inbetween", 0, "#89a02cff"],
        ["E3", 11, "r-comp-3", "Radis - désherbage complet (3)", "hoe_inbetween", 0, "#89a02cff"],
        ["E3", 12, "g-ax-1", "Germination - terre argileuse - pas de passage (1)", "skip", 0, "#ffffff"],
        ["E3", 13, "g-ax-2", "Germination - terre argileuse - pas de passage (2)", "skip", 0, "#ffffff"],
        ["E3", 14, "g-ax-3", "Germination - terre argileuse - pas de passage (3)", "skip", 0, "#ffffff"],
        ["E3", 15, "g-ap-1", "Germination - terre argileuse - passage (1)", "hoe_all", 0, "#c4eaeeff"],
        ["E3", 16, "g-ap-2", "Germination - terre argileuse - passage (2)", "hoe_all", 0, "#c4eaeeff"],
        ["E3", 17, "g-ap-3", "Germination - terre argileuse - passage (3)", "hoe_all", 0, "#c4eaeeff"],
        ["E3", 18, "g-sx-1", "Germination - terre sableuse - pas de passage (1)", "skip", 0, "#74ced8ff"],
        ["E3", 19, "g-sx-2", "Germination - terre sableuse - pas de passage (2)", "skip", 0, "#74ced8ff"],
        ["E3", 20, "g-sx-3", "Germination - terre sableuse - pas de passage (3)", "skip", 0, "#74ced8ff"],
        ["E3", 21, "g-sp-1", "Germination - terre sableuse - passage (1)", "hoe_all", 0, "#46bccbff"],
        ["E3", 22, "g-sp-2", "Germination - terre sableuse - passage (2)", "hoe_all", 0, "#46bccbff"],
        ["E3", 23, "g-sp-3", "Germination - terre sableuse - passage (3)", "hoe_all", 0, "#46bccbff"]]
    }

############################################################

history = []

def loadHistory():
    global history
    history = []
    try:
        with open("history.json", "r") as f:
            history = json.load(f)    
    except FileNotFoundError:
        history = []

        
def storeHistory():
    global history
    try:
        f = open("history.json", "w")
        f.write(json.dumps(history, indent=4, sort_keys=True))
        f.close()
    except Exception as e:
        print("Failed to write history.json!: %s" % str(e))


def addHistory(bed, zone, action):
    global history
    date = datetime.datetime.today().strftime("%Y%m%d-%H%M%S")
    history.append([bed, zone, action, date])
    storeHistory()
    

def getHistory(bed, zone):
    global history
    r = []
    for h in history:
        if h[0] == bed and h[1] == zone:
            l = list(h)
            #l[4] = datetime.strptime(l[4], "%Y%m%d-%H%M%S")
            r.append(l)
    return r

############################################################

def getBed(bed):
    return beds[bed]


def getAction(bed, zone):
    global beds
    actions = getBed(bed)
    for action in actions:
        if action[1] == zone:
            return action
    return False


def getFarmId():
    return "chat"


def farmPage():
    global beds, names
    return render_template('farm.html', names=names, beds=beds)


def zonePage(bed, zone):
    zones = getBed(bed)
    if zone <= 0:
        return farmPage()
    if zone > len(zones):
        return farmPage()
    action = getAction(bed, zone)
    if action == False:
        return render_template('error.html', message="Can't find zone %d in bed %s" % (zone, bed))
    location = {"bed": bed, "zone": zone}
    history = getHistory(bed, zone)
    return render_template('zone.html', location=location, action=action, history=history)


def weedingPage(bed, zone):
    action = getAction(bed, zone)
    location = {"bed": bed, "zone": zone}
    return render_template('weeding.html', location=location, action=action)


def homingPage(bed, zone):
    action = getAction(bed, zone)
    location = {"bed": bed, "zone": zone}
    return render_template('homing.html', location=location, action=action)


def movetoPage(bed, zone):
    zones = getBed(bed)
    if zone <= 0:
        return farmPage()
    if zone > len(zones):
        return farmPage()
    action = getAction(bed, zone)
    if action == False:
        return render_template('error.html', message="Can't find zone %d in bed %s" % (zone, bed))
    location = {"bed": bed, "zone": zone}
    return render_template('moveto.html', location=location, action=action)


def storeImage(bed, zone, label):
    action = getAction(bed, zone)
    if action == False or action[2] == "end":
        return
    zoneid = "%s-%02d" % (bed, zone)
    expid = action[2]
    name = "%s_%s_%s_DATE_%s" % (getFarmId(), zoneid, expid, label)
    print("Capturing topcam, name %s" % (name));
    r = requests.get("%s?name=%s" % (captureUrl, name))
    # FIXME handle response 
    print(r.text)

    
def storeAfterImage(bed, zone):
    storeImage(bed, zone, "after")

    
@app.route('/')
def index():
    return farmPage()


@app.route('/zone')
def zone():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    return zonePage(bed, zone)


@app.route('/moveto')
def moveto():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    return movetoPage(bed, zone)


@app.route('/cnc_status')
def cnc_status():
    global worker
    s, p = worker.getStatus()
    return jsonify(status=s, progress=p)


@app.route('/previous')
def previous():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    return zonePage(bed, zone - 1)


@app.route('/next')
def next():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    return zonePage(bed, zone + 1)

    
@app.route('/hoe_all')
def hoeAll():
    global worker
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    storeImage(bed, zone, "before")
    addHistory(bed, zone, "hoe_all")
    worker.nextRun(bed, zone, "boustrophedon", storeAfterImage)
    return weedingPage(bed, zone)
#    return movetoPage(bed, zone+1)


@app.route('/skip')
def skip():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    addHistory(bed, zone, "skip")
    storeImage(bed, zone, "before")
    return movetoPage(bed, zone+1)

   
@app.route('/homing')
def homing():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    worker.homing()
    return homingPage(bed, zone)


@app.route('/cancel')
def cancel():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    worker.cancel()
    return movetoPage(bed, zone)


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
    img = requests.get(topcamUrl + "?w=320&h=240")
    return Response(img, mimetype="image/jpeg")
#    return "ok"


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


@app.route('/tags.json')
def tags():
    tags = requests.get(tagsUrl)
    return Response(tags, mimetype="application/json")


if __name__=='__main__':
    loadHistory()
    app.run(host = '0.0.0.0', debug = False, threaded = False)
