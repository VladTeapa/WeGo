from google.oauth2 import id_token
from google.auth.transport import requests as googleReq

class TokenException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.errors = message

    def print(self): #define JSON for exception Here
        _returnValue = {
            "statusCode" : 400,
            "message" : self.errors
        }
        return _returnValue   

def verifyToken(authorizationToken):
    try:
        CLIENT_ID = "656198391888-1md06u7j1q7qnakbplobqaij3t7d2ifm.apps.googleusercontent.com"
        idinfo = id_token.verify_oauth2_token(authorizationToken, googleReq.Request(), CLIENT_ID)
        userID = idinfo["sub"]
        userMail = idinfo["email"]
        userName = idinfo["name"]
        return ["google", userID, userMail, userName]
    except ValueError:
        raise TokenException("Invalid token was provided!")
