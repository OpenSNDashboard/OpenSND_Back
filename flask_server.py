from flask_api import FlaskAPI, status, exceptions
from flask import request

import os
import json
from datetime import datetime

from DAOs.main_dao import DAO

app = FlaskAPI("OpenSND")
app.config['DEBUG'] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

dao = DAO()

def exists(id):
    dashboards = os.listdir('./dashboards')
    for dashboard in dashboards:
        if dashboard.split('.')[0] == id:
            return True
    return False


def getNextId():
    maxId = 0
    dashboards = os.listdir('./dashboards')
    for dashboard in dashboards:
        id = int(dashboard.split('.')[0])
        if id > maxId:
            maxId = id
    return maxId + 1


def isValidSettings(settings):
    neededKeys = ["reddit", "twitter"]
    for key in neededKeys:
        if key not in settings.keys():
            return False

    return True


def isValidDashboard(dashboard):
    neededKeys = ["name", "reddit", "twitter"]
    for key in neededKeys:
        if key not in dashboard.keys():
            return False

    if not isinstance(dashboard["reddit"], list):
        return False
    redditKeys = ["name", "filter"]
    filters = ["hot", "top", "controversial", "new", "random"]
    for subreddit in dashboard["reddit"]:
        if not isinstance(subreddit, dict):
            return False
        for key in redditKeys:
            if key not in subreddit:
                return False
        if subreddit["filter"] not in filters:
            return False

    if not isinstance(dashboard["twitter"], list):
        return False
    # TODO: vérification twitter

    # SINON
    return True


# Configuration générale
# GET /api/config
# PUT /api/config "Content-type: application/json" main_config.json
@app.route('/api/config', methods=['GET', 'PUT'])
def manageMainConfig():
    # RÉCUPÉRATION DE LA MAIN CONFIG
    if request.method == 'GET':
        with open('settings.json', 'r') as settings_file:
            settings = json.load(settings_file)
            return settings, status.HTTP_200_OK

    # MODIFICATION DE LA MAIN CONFIG
    elif request.method == 'PUT':
        # ça je trouve ça un peu crade, il doit y avoir un meilleur moyen
        if "application/json" in request.headers["content-type"]:
            if isValidSettings(request.json):
                with open('settings.json', 'w') as settings_file:
                    # Prettify le json avant de l'écrire dans le fichier
                    json.dump(request.json, settings_file, indent=4)
                return request.json, status.HTTP_200_OK

        raise exceptions.ParseError()


# GET /api/dashboards
@app.route('/api/dashboards', methods=['GET'])
def getAllDashboards():
    data = {}

    # RÉCUPÉRATION DE TOUS LES DASHBOARDS
    dashboards = os.listdir('./dashboards')
    for dashboard in dashboards:
        print(dashboard)
        # TODO: vérifier si les fichiers sont bien des config json de dashboards
        id = dashboard.split('.')[0]
        with open('./dashboards/' + dashboard, 'r') as dashboard_settings:
            data[id] = json.load(dashboard_settings)

    return data, status.HTTP_200_OK


# POST /api/dashboards "Content-type: application/json" dashboard.json
@app.route('/api/dashboards', methods=['POST'])
def addDashboard():
    # CRÉATION DE DASHBOARD
    if "application/json" in request.headers["content-type"]:
        if isValidDashboard(request.json):
            id = str(getNextId())
            with open('./dashboards/' + id + '.json', 'w') as dashboard_settings:
                json.dump(request.json, dashboard_settings, indent=4)
            dao.parseDashboard(id)
            return request.json, status.HTTP_201_CREATED

    raise exceptions.ParseError()


# GET /api/dashboards/<id>
# PUT /api/dashboards/<id> "Content-type: application/json" dashboard.json
# DELETE /api/dashboards/<id>
@app.route('/api/dashboards/<string:id>', methods=['GET', 'PUT', 'DELETE'])
def manageDashboards(id):
    if not exists(id):
        raise exceptions.NotFound()

    # RÉCUPÉRATION DE DASHBOARD
    if request.method == 'GET':
        with open('./dashboards/' + id + '.json', 'r') as dashboard_settings:
            data = json.load(dashboard_settings)
            return data, status.HTTP_200_OK

    # MODIFICATION DE DASHBOARD
    elif request.method == 'PUT':
        # ça je trouve ça un peu crade, il doit y avoir un meilleur moyen
        if "application/json" in request.headers["content-type"]:
            if isValidDashboard(request.json):
                with open('./dashboards/' + id + '.json', 'w') as dashboard_settings:
                    # TODO: Prettify le json avant de l'écrire dans le fichier
                    json.dump(request.json, dashboard_settings, indent=4)
                dao.parseDashboard(id)
                return request.json, status.HTTP_200_OK

        raise exceptions.ParseError()

    # SUPPRESSION DE DASHBOARD
    elif request.method == 'DELETE':
        os.remove('./dashboards/' + id + '.json')
        dao.parseDashboard(id)
        return '', status.HTTP_204_NO_CONTENT


# GET /api/dashboards/<id>/content?since=<unix_timestamp>
@app.route('/api/dashboards/<string:id>/content', methods=['GET'])
def getContent(id):
    if not exists(id):
        raise exceptions.NotFound()

    if "since" in request.args:
        # On pourrait aussi utiliser datetime.fromisoformat(str) mais ça me semble risqué
        since = datetime.fromtimestamp(int(request.args['since']))
    else:
        since = None # datetime.now()

    data = dao.getContent(id=id, since=since)

    return data, status.HTTP_200_OK


# --------- MAIN ---------
if __name__ == "__main__":
    app.run()
