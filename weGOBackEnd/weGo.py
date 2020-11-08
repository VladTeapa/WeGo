import base64
import os
import json

import requests
import time
from flask import Flask, request, Response
from Modules.databaseModule import *
from Modules.tokenModule import *
from Modules.findTipsModule import *

app = Flask(__name__)

def createResponse(_returnValue, statusCode = 200):
    response = Response(response=json.dumps(_returnValue), status=statusCode, mimetype="application/json")
    response.headers["Content-Type"] = "application/json"
    response.headers["Accept-Charset"] = "utf-8"
    return response

def makeAuth():
    Database = DBConnection()
    authorizationToken = request.headers.get("Authorization")
    userData = []
    if (authorizationToken != None):
        userData = verifyToken(authorizationToken)
    else:
        userData = [request.json["operation"],
                    request.json["email"],
                    request.json["password"]]
        if(request.json["operation"] == "signUp"):
            userData.append(request.json["userName"])
    #Check if user has visited that place
    Database.checkUser(userData)
    return Database

@app.route('/register', methods=["POST"])
def runTest():
    try:
        Database = makeAuth()
        return createResponse({
            "statusCode" : 200,
            "message" : "Success!"
        })
    except Exception as ex:
        return createResponse(ex.print(), 422)


@app.route('/achievements', methods=["GET"])
def returnAchievements():
    try:
        #Database = DBConnection()
        #Database.UserID = 1
        Database = makeAuth()
        #authorizationToken = request.headers.get("Authorization")
        #userData = verifyToken(authorizationToken)
        #Database.checkUser(userData)
        _returnValue = Database.getAchievements()
        print(_returnValue)
        return createResponse({
                    "statusCode" : 200,
                    "message" : _returnValue
                })
    except Exception as ex:     
        return createResponse(ex.print(), 422)

@app.route('/getTips', methods=["POST"])
def returnTips():
    try:

        Database = makeAuth()
        #Database = DBConnection()
        LocationName = Database.isVisited(request.json["LocationID"])

        if(LocationName != None):
            return createResponse({
                        "statusCode" : 200,
                        "message" : findDescriptions(LocationName)
                    })
        else:
            return createResponse("Location was no visited!", 410)
    except Exception as ex:     
        return createResponse("Error!", 500)
    except UnicodeDecodeError as ex:
        return createResponse("Error!", 500)


@app.route('/addVisitedLocation', methods=["POST"])
def addVisited():
    try:

        Database = makeAuth()
        #Database = DBConnection()
        Database.addVisitedLocation(request.json)

        return createResponse({
                    "statusCode" : 200,
                    "message" : "Success!"
                })
    except Exception as ex:     
        return createResponse("Error!", 405)       
    except UnicodeDecodeError as ex:
        return createResponse("Error!", 500)

@app.route('/getCovidCases', methods=["POST"])
def getCovidCases():
    try:
        #Specify message format @VladTeapa
        print(getCovidStatus(request.json["Country"]))
        return createResponse({
                    "statusCode" : 200,
                    "message" : "Success!"
                })
    except Exception as ex:     
        return createResponse(ex.print(), 405) 

@app.route('/getLeaderboard', methods=["GET"])
def getLeaderBoard():
    try:

        Database = makeAuth()
        #Database = DBConnection()
        #Database.UserID = 1
        return createResponse({
                    "statusCode" : 200,
                    "message" : Database.getLeaderBoard(request.headers.get("Country"))
                })
    except Exception as ex:     
        return createResponse(ex.print(), 405) 


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=80)
    #app.run(debug=True, port=80)
