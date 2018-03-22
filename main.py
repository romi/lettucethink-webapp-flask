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

app = Flask(__name__)

farm = "chat"
actions = [
    ["I1", 1, "ri-man-1", "apr", "Radis - manuel (1)", "skip"],
    ["I1", 2, "ri-man-2", "apr", "Radis - manuel (2)", "skip"],
    ["I1", 3, "ri-man-3", "apr", "Radis - manuel (3)", "skip"],
    ["I1", 4, "ri-x-1", "apr", "Radis - pas de passage (1)", "skip"],
    ["I1", 5, "ri-x-2", "apr", "Radis - pas de passage (2)", "skip"],
    ["I1", 6, "ri-x-3", "apr", "Radis - pas de passage (3)", "skip"],
    ["I1", 7, "ri-sel-1", "apr", "Radis - désherbage sélectif (1)", "hoe_weeds"],
    ["I1", 8, "ri-sel-2", "apr", "Radis - désherbage sélectif (2)", "hoe_weeds"],
    ["I1", 9, "ri-sel-3", "apr", "Radis - désherbage sélectif (3)", "hoe_weeds"],
    ["I1", 10, "ri-comp-1", "apr", "Radis - désherbage complet (1)", "hoe_inbetween"],
    ["I1", 11, "ri-comp-2", "apr", "Radis - désherbage complet (2)", "hoe_inbetween"],
    ["I1", 12, "ri-comp-3", "apr", "Radis - désherbage complet (3)", "hoe_inbetween"],
    ["I1", 13, "fi-0x-1", "apr", "Fréquence - pas de passage (1)", "skip"],
    ["I1", 14, "fi-0x-2", "apr", "Fréquence - pas de passage (2)", "skip"],
    ["I1", 15, "fi-0x-3", "apr", "Fréquence - pas de passage (3)", "skip"],
    ["I1", 16, "fi-05x-1", "apr", "Fréquence - 1x / 2 sem. (1)", "hoe_all"],
    ["I1", 17, "fi-05x-2", "apr", "Fréquence - 1x / 2 sem. (2)", "hoe_all"],
    ["I1", 18, "fi-05x-3", "apr", "Fréquence - 1x / 2 sem. (3)", "hoe_all"],
    ["I1", 19, "fi-1x-1", "apr", "Fréquence - 1x / sem. (1)", "hoe_all"],
    ["I1", 20, "fi-1x-2", "apr", "Fréquence - 1x / sem. (2)", "hoe_all"],
    ["I1", 21, "fi-1x-3", "apr", "Fréquence - 1x / sem. (3)", "hoe_all"],
    ["I1", 22, "fi-2x-1", "apr", "Fréquence - 2x / sem. (1)", "hoe_all"],
    ["I1", 23, "fi-2x-2", "apr", "Fréquence - 2x / sem. (2)", "hoe_all"],
    ["I1", 24, "fi-2x-3", "apr", "Fréquence - 2x / sem. (3)", "hoe_all"],
    ["I1", 25, "gi-ax-1", "apr", "Germination - terre argileuse - pas de passage (1)", "skip"],
    ["I1", 26, "gi-ax-2", "apr", "Germination - terre argileuse - pas de passage (2)", "skip"],
    ["I1", 27, "gi-ax-3", "apr", "Germination - terre argileuse - pas de passage (3)", "skip"],
    ["I1", 28, "gi-ap-1", "apr", "Germination - terre argileuse - passage (1)", "hoe_all"],
    ["I1", 29, "gi-ap-2", "apr", "Germination - terre argileuse - passage (2)", "hoe_all"],
    ["I1", 30, "gi-ap-3", "apr", "Germination - terre argileuse - passage (3)", "hoe_all"],
    ["I1", 31, "gi-sx-1", "apr", "Germination - terre sableuse - pas de passage (1)", "skip"],
    ["I1", 32, "gi-sx-2", "apr", "Germination - terre sableuse - pas de passage (2)", "skip"],
    ["I1", 33, "gi-sx-3", "apr", "Germination - terre sableuse - pas de passage (3)", "skip"],
    ["I1", 34, "gi-sp-1", "apr", "Germination - terre sableuse - passage (1)", "hoe_all"],
    ["I1", 35, "gi-sp-2", "apr", "Germination - terre sableuse - passage (2)", "hoe_all"],
    ["I1", 36, "gi-sp-3", "apr", "Germination - terre sableuse - passage (3)", "hoe_all"],
    ["I1", 37, "end"],
    ["E1", 1, "re-man-1", "apr", "Radis - manuel (1)", "skip"],
    ["E1", 2, "re-man-2", "apr", "Radis - manuel (2)", "skip"],
    ["E1", 3, "re-man-3", "apr", "Radis - manuel (3)", "skip"],
    ["E1", 4, "re-x-1", "apr", "Radis - pas de passage (1)", "skip"],
    ["E1", 5, "re-x-2", "apr", "Radis - pas de passage (2)", "skip"],
    ["E1", 6, "re-x-3", "apr", "Radis - pas de passage (3)", "skip"],
    ["E1", 7, "re-sel-1", "apr", "Radis - désherbage sélectif (1)", "hoe_weeds"],
    ["E1", 8, "re-sel-2", "apr", "Radis - désherbage sélectif (2)", "hoe_weeds"],
    ["E1", 9, "re-sel-3", "apr", "Radis - désherbage sélectif (3)", "hoe_weeds"],
    ["E1", 10, "re-comp-1", "apr", "Radis - désherbage complet (1)", "hoe_inbetween"],
    ["E1", 11, "re-comp-2", "apr", "Radis - désherbage complet (2)", "hoe_inbetween"],
    ["E1", 12, "re-comp-3", "apr", "Radis - désherbage complet (3)", "hoe_inbetween"],
    ["E1", 13, "fe-0x-1", "apr", "Fréquence - pas de passage (1)", "skip"],
    ["E1", 14, "fe-0x-2", "apr", "Fréquence - pas de passage (2)", "skip"],
    ["E1", 15, "fe-0x-3", "apr", "Fréquence - pas de passage (3)", "skip"],
    ["E1", 16, "fe-05x-1", "apr", "Fréquence - 1x / 2 sem. (1)", "hoe_all"],
    ["E1", 17, "fe-05x-2", "apr", "Fréquence - 1x / 2 sem. (2)", "hoe_all"],
    ["E1", 18, "fe-05x-3", "apr", "Fréquence - 1x / 2 sem. (3)", "hoe_all"],
    ["E1", 19, "fe-1x-1", "apr", "Fréquence - 1x / sem. (1)", "hoe_all"],
    ["E1", 20, "fe-1x-2", "apr", "Fréquence - 1x / sem. (2)", "hoe_all"],
    ["E1", 21, "fe-1x-3", "apr", "Fréquence - 1x / sem. (3)", "hoe_all"],
    ["E1", 22, "fe-2x-1", "apr", "Fréquence - 2x / sem. (1)", "hoe_all"],
    ["E1", 23, "fe-2x-2", "apr", "Fréquence - 2x / sem. (2)", "hoe_all"],
    ["E1", 24, "fe-2x-3", "apr", "Fréquence - 2x / sem. (3)", "hoe_all"],
    ["E1", 25, "pe-x-1", "apr", "Chénopodes", "skip"],
    ["E1", 26, "end"],    
    ["E3", 1, "re-man-1", "apr", "Radis - manuel (1)", "skip"],
    ["E3", 2, "re-man-2", "apr", "Radis - manuel (2)", "skip"],
    ["E3", 3, "re-man-3", "apr", "Radis - manuel (3)", "skip"],
    ["E3", 4, "re-x-1", "apr", "Radis - pas de passage (1)", "skip"],
    ["E3", 5, "re-x-2", "apr", "Radis - pas de passage (2)", "skip"],
    ["E3", 6, "re-x-3", "apr", "Radis - pas de passage (3)", "skip"],
    ["E3", 7, "re-sel-1", "apr", "Radis - désherbage sélectif (1)", "hoe_weeds"],
    ["E3", 8, "re-sel-2", "apr", "Radis - désherbage sélectif (2)", "hoe_weeds"],
    ["E3", 9, "re-sel-3", "apr", "Radis - désherbage sélectif (3)", "hoe_weeds"],
    ["E3", 10, "re-comp-1", "apr", "Radis - désherbage complet (1)", "hoe_inbetween"],
    ["E3", 11, "re-comp-2", "apr", "Radis - désherbage complet (2)", "hoe_inbetween"],
    ["E3", 12, "re-comp-3", "apr", "Radis - désherbage complet (3)", "hoe_inbetween"],
    ["E3", 13, "ge-ax-1", "apr", "Germination - terre argileuse - pas de passage (1)", "skip"],
    ["E3", 14, "ge-ax-2", "apr", "Germination - terre argileuse - pas de passage (2)", "skip"],
    ["E3", 15, "ge-ax-3", "apr", "Germination - terre argileuse - pas de passage (3)", "skip"],
    ["E3", 16, "ge-ap-1", "apr", "Germination - terre argileuse - passage (1)", "hoe_all"],
    ["E3", 17, "ge-ap-2", "apr", "Germination - terre argileuse - passage (2)", "hoe_all"],
    ["E3", 18, "ge-ap-3", "apr", "Germination - terre argileuse - passage (3)", "hoe_all"],
    ["E3", 19, "ge-sx-1", "apr", "Germination - terre sableuse - pas de passage (1)", "skip"],
    ["E3", 20, "ge-sx-2", "apr", "Germination - terre sableuse - pas de passage (2)", "skip"],
    ["E3", 21, "ge-sx-3", "apr", "Germination - terre sableuse - pas de passage (3)", "skip"],
    ["E3", 22, "ge-sp-1", "apr", "Germination - terre sableuse - passage (1)", "hoe_all"],
    ["E3", 23, "ge-sp-2", "apr", "Germination - terre sableuse - passage (2)", "hoe_all"],
    ["E3", 24, "ge-sp-3", "apr", "Germination - terre sableuse - passage (3)", "hoe_all"],
    ["E3", 25, "ae-x-1", "apr", "Arabidopsis", "skip"],
    ["E3", 26, "end"]]

def getAction(bed, zone):
    for action in actions:
        if action[0] == bed and action[1] == zone:
            return action
    return False

def zonePage(bed, zone):
    action = getAction(bed, zone)
    if action == False:
        return render_template('error.html', message="Can't find zone %d in bed %s" % (zone, bed))
    if action[2] == "end":
        return render_template('farm.html')
    location = {"bed": bed, "zone": zone}
    return render_template('zone.html', location=location, action=action)



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
    return zonePage(bed, zone + 1)

@app.route('/hoe_inbetween')
def hoeInBetween():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    return zonePage(bed, zone + 1)

@app.route('/hoe_weeds')
def hoeWeeds():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    return zonePage(bed, zone + 1)

@app.route('/hoe_seeds')
def hoeSeeds():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    return zonePage(bed, zone + 1)

@app.route('/skip')
def skip():
    bed = request.args["bed"]
    zone = int(request.args["zone"])
    return zonePage(bed, zone + 1)

@app.route('/boustro')
def boustro():
    return "ok"
   
@app.route('/homing')
def homing():
    print("homing")
    return "ok"

if __name__=='__main__':
   app.run(host = '0.0.0.0', debug = True)
