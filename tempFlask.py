import os
import json

from flask import Flask, request, jsonify
from tempDB import tempDB
from bson.json_util import dumps
from datetime import datetime, timedelta

app = Flask(__name__)


def changeJSON(jsonResult):
    resid = 0
    for res in jsonResult:
        time = datetime.fromtimestamp(res['time']['$date'] / 1e3)

        # Change json result
        del res['_id']
        del res['time']
        res['id'] = resid
        res['time'] = time
        resid += 1


@app.route('/fetchAll', methods=['GET'])
def fetchAll():
    results = json.loads(dumps(temp.findAll()))
    changeJSON(results)

    return jsonify(results)


@app.route('/fetchTime', methods=['GET'])
def fetchTime():
    time = int(request.args.get('time'))
    now = datetime.now()

    finalTime = (now - timedelta(hours=time))

    results = json.loads(dumps(temp.find_byDate(finalTime)))
    changeJSON(results)
    
    return jsonify(results)


@app.route('/fetchRecent', methods=['GET'])
def fetchRecent():
    results = json.loads(dumps(temp.findRecent()))
    changeJSON(results)
    print(results)

    return jsonify(results)


@app.route('/fetchTemps', methods=['GET'])
def fetchTempLists():
    results = temp.findAll()

    ctemps = []
    ftemps = []
    for res in results:
        ctemps.append(res['ctemp'])
        ftemps.append(res['ftemp'])

    return jsonify({'ftemps': ftemps, 'ctemps': ctemps})


@app.route('/changeRead', methods=['POST'])
def changeRead():
    currentUnit = ['fahr', 'cels']
    currentOperator = ['greater', 'less']

    read = request.json
    read['unit'] = currentUnit[read['selectUnit']]
    read['operator'] = currentOperator[read['tempOperator']]
    del read['selectUnit']
    del read['tempOperator']
    newAlert = { '$set': read }

    temp.updateAlert(newAlert)

    return jsonify(read)


@app.route('/fetchSettings', methods=['GET'])
def fetchSettings():
    currentUnit = ['fahr', 'cels']
    alert = temp.getAlert()

    alert['selectUnit'] = currentUnit.index(alert['unit'])
    del alert['unit']
    del alert['_id']
    del alert['name']

    print(alert)

    return jsonify(alert)


if __name__ == '__main__':
    temp = tempDB('mylib', 'temperatures', 'read')
    app.run(host='0.0.0.0', debug=True)