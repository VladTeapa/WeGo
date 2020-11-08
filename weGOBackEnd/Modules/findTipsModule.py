import re
import requests

class TipsExceptions(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.errors = message

    def print(self): #define JSON for exception Here
        _returnValue = {
            "statusCode" : 400,
            "message" : self.errors
        }
        return _returnValue   

def findDescriptions(location):
    try:
        requestURL = "http://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exlimit=max&explaintext&exintro&titles=" + location + "&redirects="
        #Make request

        details = requests.get(requestURL).json()["query"]
        if(next(iter(details["pages"])) == '-1'):
            return "Could not find anything about given location."
            #raise TipsExceptions("Could not find anything about given location.")
        else:
            details = (details["pages"][next(iter(details["pages"]))]["extract"])
            #Remove () and []
            details = re.sub("[\(\[].*?[\)\]]", "", details)
            details = details.replace("(", "")
            details = details.replace(")", "")
            details = details.replace("[", "")
            details = details.replace("]", "")
            #Keep only some sentences

            sentencesList = details.split(".")
            _returnValue = ""
            #print(sentencesList)
            for _ in sentencesList:
                _returnValue = _returnValue + _ + ". "
                if(len(_returnValue) > 60):
                    break
            _returnValue = ' '.join(_returnValue.split())

            return _returnValue
            #If script did not find anything throw error

    except ValueError:
        return "Could not find anything about given location."


def getCovidStatus(targetCountry):

    try:
        requestURL = "https://api.covid19api.com/summary"
        covidCasesTotal = requests.get(requestURL).json()["Countries"]

        for _ in covidCasesTotal:
            if (_["Country"] == targetCountry):
                return _

    except ValueError:
        raise TipsExceptions("Could not perform GET request!")
