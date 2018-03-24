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
from flask import Flask, render_template, Response, request, redirect
import requests
import datetime

imgdir = "/tmp"
topcamUrl = "http://lettucethink-topcam.local:10000/image.jpg"

app = Flask(__name__)

def getAction(bed, zone):
    actions = [
        ["I1", 1, "r-man-1", "Radis - manuel (1)", "skip"],
        ["I1", 2, "r-man-2", "Radis - manuel (2)", "skip"],
        ["I1", 3, "r-man-3", "Radis - manuel (3)", "skip"],
        ["I1", 4, "r-x-1", "Radis - pas de passage (1)", "skip"],
        ["I1", 5, "r-x-2", "Radis - pas de passage (2)", "skip"],
        ["I1", 6, "r-x-3", "Radis - pas de passage (3)", "skip"],
        ["I1", 7, "r-sel-1", "Radis - désherbage sélectif (1)", "hoe_weeds"],
        ["I1", 8, "r-sel-2", "Radis - désherbage sélectif (2)", "hoe_weeds"],
        ["I1", 9, "r-sel-3", "Radis - désherbage sélectif (3)", "hoe_weeds"],
        ["I1", 10, "r-comp-1", "Radis - désherbage complet (1)", "hoe_inbetween"],
        ["I1", 11, "r-comp-2", "Radis - désherbage complet (2)", "hoe_inbetween"],
        ["I1", 12, "r-comp-3", "Radis - désherbage complet (3)", "hoe_inbetween"],
        ["I1", 13, "f-0x-1", "Fréquence - pas de passage (1)", "skip"],
        ["I1", 14, "f-0x-2", "Fréquence - pas de passage (2)", "skip"],
        ["I1", 15, "f-0x-3", "Fréquence - pas de passage (3)", "skip"],
        ["I1", 16, "f-05x-1", "Fréquence - 1x / 2 sem. (1)", "hoe_all"],
        ["I1", 17, "f-05x-2", "Fréquence - 1x / 2 sem. (2)", "hoe_all"],
        ["I1", 18, "f-05x-3", "Fréquence - 1x / 2 sem. (3)", "hoe_all"],
        ["I1", 19, "f-1x-1", "Fréquence - 1x / sem. (1)", "hoe_all"],
        ["I1", 20, "f-1x-2", "Fréquence - 1x / sem. (2)", "hoe_all"],
        ["I1", 21, "f-1x-3", "Fréquence - 1x / sem. (3)", "hoe_all"],
        ["I1", 22, "f-2x-1", "Fréquence - 2x / sem. (1)", "hoe_all"],
        ["I1", 23, "f-2x-2", "Fréquence - 2x / sem. (2)", "hoe_all"],
        ["I1", 24, "f-2x-3", "Fréquence - 2x / sem. (3)", "hoe_all"],
        ["I1", 25, "g-ax-1", "Germination - terre argileuse - pas de passage (1)", "skip"],
        ["I1", 26, "g-ax-2", "Germination - terre argileuse - pas de passage (2)", "skip"],
        ["I1", 27, "g-ax-3", "Germination - terre argileuse - pas de passage (3)", "skip"],
        ["I1", 28, "g-ap-1", "Germination - terre argileuse - passage (1)", "hoe_all"],
        ["I1", 29, "g-ap-2", "Germination - terre argileuse - passage (2)", "hoe_all"],
        ["I1", 30, "g-ap-3", "Germination - terre argileuse - passage (3)", "hoe_all"],
        ["I1", 31, "g-sx-1", "Germination - terre sableuse - pas de passage (1)", "skip"],
        ["I1", 32, "g-sx-2", "Germination - terre sableuse - pas de passage (2)", "skip"],
        ["I1", 33, "g-sx-3", "Germination - terre sableuse - pas de passage (3)", "skip"],
        ["I1", 34, "g-sp-1", "Germination - terre sableuse - passage (1)", "hoe_all"],
        ["I1", 35, "g-sp-2", "Germination - terre sableuse - passage (2)", "hoe_all"],
        ["I1", 36, "g-sp-3", "Germination - terre sableuse - passage (3)", "hoe_all"],
        ["I1", 37, "end"],
        ["E1", 1, "r-man-1", "Radis - manuel (1)", "skip"],
        ["E1", 2, "r-man-2", "Radis - manuel (2)", "skip"],
        ["E1", 3, "r-man-3", "Radis - manuel (3)", "skip"],
        ["E1", 4, "r-x-1", "Radis - pas de passage (1)", "skip"],
        ["E1", 5, "r-x-2", "Radis - pas de passage (2)", "skip"],
        ["E1", 6, "r-x-3", "Radis - pas de passage (3)", "skip"],
        ["E1", 7, "r-sel-1", "Radis - désherbage sélectif (1)", "hoe_weeds"],
        ["E1", 8, "r-sel-2", "Radis - désherbage sélectif (2)", "hoe_weeds"],
        ["E1", 9, "r-sel-3", "Radis - désherbage sélectif (3)", "hoe_weeds"],
        ["E1", 10, "r-comp-1", "Radis - désherbage complet (1)", "hoe_inbetween"],
        ["E1", 11, "r-comp-2", "Radis - désherbage complet (2)", "hoe_inbetween"],
        ["E1", 12, "r-comp-3", "Radis - désherbage complet (3)", "hoe_inbetween"],
        ["E1", 13, "f-0x-1", "Fréquence - pas de passage (1)", "skip"],
        ["E1", 14, "f-0x-2", "Fréquence - pas de passage (2)", "skip"],
        ["E1", 15, "f-0x-3", "Fréquence - pas de passage (3)", "skip"],
        ["E1", 16, "f-05x-1", "Fréquence - 1x / 2 sem. (1)", "hoe_all"],
        ["E1", 17, "f-05x-2", "Fréquence - 1x / 2 sem. (2)", "hoe_all"],
        ["E1", 18, "f-05x-3", "Fréquence - 1x / 2 sem. (3)", "hoe_all"],
        ["E1", 19, "f-1x-1", "Fréquence - 1x / sem. (1)", "hoe_all"],
        ["E1", 20, "f-1x-2", "Fréquence - 1x / sem. (2)", "hoe_all"],
        ["E1", 21, "f-1x-3", "Fréquence - 1x / sem. (3)", "hoe_all"],
        ["E1", 22, "f-2x-1", "Fréquence - 2x / sem. (1)", "hoe_all"],
        ["E1", 23, "f-2x-2", "Fréquence - 2x / sem. (2)", "hoe_all"],
        ["E1", 24, "f-2x-3", "Fréquence - 2x / sem. (3)", "hoe_all"],
        ["E1", 25, "p-x-1", "Chénopodes", "skip"],
        ["E1", 26, "end"],    
        ["E3", 1, "r-man-1", "Radis - manuel (1)", "skip"],
        ["E3", 2, "r-man-2", "Radis - manuel (2)", "skip"],
        ["E3", 3, "r-man-3", "Radis - manuel (3)", "skip"],
        ["E3", 4, "r-x-1", "Radis - pas de passage (1)", "skip"],
        ["E3", 5, "r-x-2", "Radis - pas de passage (2)", "skip"],
        ["E3", 6, "r-x-3", "Radis - pas de passage (3)", "skip"],
        ["E3", 7, "r-sel-1", "Radis - désherbage sélectif (1)", "hoe_weeds"],
        ["E3", 8, "r-sel-2", "Radis - désherbage sélectif (2)", "hoe_weeds"],
        ["E3", 9, "r-sel-3", "Radis - désherbage sélectif (3)", "hoe_weeds"],
        ["E3", 10, "r-comp-1", "Radis - désherbage complet (1)", "hoe_inbetween"],
        ["E3", 11, "r-comp-2", "Radis - désherbage complet (2)", "hoe_inbetween"],
        ["E3", 12, "r-comp-3", "Radis - désherbage complet (3)", "hoe_inbetween"],
        ["E3", 13, "g-ax-1", "Germination - terre argileuse - pas de passage (1)", "skip"],
        ["E3", 14, "g-ax-2", "Germination - terre argileuse - pas de passage (2)", "skip"],
        ["E3", 15, "g-ax-3", "Germination - terre argileuse - pas de passage (3)", "skip"],
        ["E3", 16, "g-ap-1", "Germination - terre argileuse - passage (1)", "hoe_all"],
        ["E3", 17, "g-ap-2", "Germination - terre argileuse - passage (2)", "hoe_all"],
        ["E3", 18, "g-ap-3", "Germination - terre argileuse - passage (3)", "hoe_all"],
        ["E3", 19, "g-sx-1", "Germination - terre sableuse - pas de passage (1)", "skip"],
        ["E3", 20, "g-sx-2", "Germination - terre sableuse - pas de passage (2)", "skip"],
        ["E3", 21, "g-sx-3", "Germination - terre sableuse - pas de passage (3)", "skip"],
        ["E3", 22, "g-sp-1", "Germination - terre sableuse - passage (1)", "hoe_all"],
        ["E3", 23, "g-sp-2", "Germination - terre sableuse - passage (2)", "hoe_all"],
        ["E3", 24, "g-sp-3", "Germination - terre sableuse - passage (3)", "hoe_all"],
        ["E3", 25, "a-x-1", "Arabidopsis", "skip"],
        ["E3", 26, "end"]]
    for action in actions:
        if action[0] == bed and action[1] == zone:
            return action
    return False


def getFarmId():
    return "chat"


def zonePage(bed, zone):
    action = getAction(bed, zone)
    if action == False:
        return render_template('error.html', message="Can't find zone %d in bed %s" % (zone, bed))
    if action[2] == "end":
        return render_template('farm.html')
    location = {"bed": bed, "zone": zone}
    return render_template('zone.html', location=location, action=action)


def storeImage(bed, zone, label):
    action = getAction(bed, zone)
    if action == False or action[2] == "end":
        return
    date = datetime.datetime.today().strftime("%Y%m%d-%H%M%S")
    zoneid = "%s-%02d" % (bed, zone)
    expid = action[2]
    path = "%s/%s_%s_%s_%s_%s.jpg" % (imgdir, date, getFarmId(), zoneid, expid, label)
    print("Saving topcam image to %s" % (path));
    r = requests.get(topcamUrl)
    file = open(path, "wb")
    file.write(r.content);
    file.close()
    
    
@app.route('/')
def index():
    return render_template('farm.html')

@app.route('/zone')
def zone():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    return zonePage(bed, zone)

@app.route('/back')
def back():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    if zone > 1:
        return zonePage(bed, zone - 1)
    else:
        return render_template('farm.html')

@app.route('/hoe_all')
def hoeAll():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    storeImage(bed, zone, "before")
    return zonePage(bed, zone + 1)

@app.route('/hoe_inbetween')
def hoeInBetween():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    storeImage(bed, zone, "before")
    return zonePage(bed, zone + 1)

@app.route('/hoe_weeds')
def hoeWeeds():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    storeImage(bed, zone, "before")
    return zonePage(bed, zone + 1)

@app.route('/hoe_seeds')
def hoeSeeds():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    storeImage(bed, zone, "before")
    return zonePage(bed, zone + 1)

@app.route('/skip')
def skip():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    storeImage(bed, zone, "before")
    return zonePage(bed, zone + 1)

@app.route('/boustro')
def boustro():
    return "ok"
   
@app.route('/homing')
def homing():
    print("homing")
    return "ok"

@app.route('/topcam.jpg')
def topcam():
    img = requests.get(topcamUrl + "?w=320&h=240")
    return Response(img, mimetype="image/jpeg")

if __name__=='__main__':
   app.run(host = '0.0.0.0', debug = True)
