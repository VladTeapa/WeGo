import mariadb
import sys
import json
import secrets

class DBConnection:

    def __init__(self):
        try:
            self.conn = mariadb.connect(
                user="weGO",
                password="",
                host="localhost",
                database="weGO",
                port=3306)
            #make sure we have all tables in here    
            self.cursor = self.conn.cursor()
            self.UserID = -1
            self.checkTables()
        except mariadb.Error as e:
            raise DBException('Error while opening the database Conn')
        return None

    def myfunc(self):
        print("Hello my name is " + self.name)

    def checkTables(self):
        file = open('Modules/schema.sql',mode='r')
        allTables = file.read()
        file.close()
        allTables = allTables.split(";")
        try:
            for _ in allTables:
                if( _ != "\n" and _ != ""): 
                    self.cursor.execute(_)
            self.conn.commit()
        except mariadb.Error as e:
            print(e)
            self.conn.rollback()
            raise DBException('Error while DB config')

    def __del__(self): 
        self.conn.close()

    def checkUser(self, args):
        if(self.UserID == -1):
            try:
                cursor = self.cursor
                if(args[0] == "google"):
                    cursor.execute("SELECT ID FROM Users \
                    WHERE Email = ? and OauthID = ?;", (args[2], args[1],))
                    #If user does not exist 
                    response = cursor.fetchone()
                    if(response == None):
                        #Create user ["google", userID, userMail, userName]
                        randomPassword = secrets.token_hex(32)
                        cursor.execute("INSERT INTO Users (OauthID, Username, Password, Email ) VALUES \
                            (?, ?, ?, ?)", (args[1], args[3], randomPassword, args[2]))
                        self.conn.commit()
                        return self.checkUser(args)
                    else:
                        self.UserID = response[0]
                        return
                elif (args[0] == "login"):
                    #Check if user exists and password matches
                    cursor.execute("SELECT ID FROM Users \
                    WHERE Email = ? and Password = ?;", (args[1], args[2],))
                    response = cursor.fetchone()                
                    if(response == None):
                        raise DBException('Wrong cridentials!')
                    else:
                        self.UserID = response[0]
                        return 

                elif (args[0] == "signUp"):
                    #Check if another user with same email exists
                    cursor.execute("SELECT ID FROM Users \
                    WHERE Email = ?;", (args[1],))
                    response = cursor.fetchone()
                    if(response == None):
                        #If ser does not have an account yet, create it
                        cursor.execute("INSERT INTO Users (Username, Password, Email ) VALUES \
                            (?, ?, ?)", (args[3], args[2], args[1]))
                        self.conn.commit()
                        newArgs = ["login", args[1], args[2]]
                        return self.checkUser(newArgs)
                    else:
                        raise DBException('Account already exists!')
                    
            except mariadb.Error as e:
                self.conn.rollback()
                raise DBException('Error while getting User Information')


    def getAchievements(self):
        if(self.UserID >= 0):

            #Get current user Achievements
            _returnValue = []

            cursor = self.cursor
            cursor.execute("SELECT \
            Achievements.ID, Achievements.Name, Achievements.Description, Users_Achievements.Number, Achievements.Target \
            FROM Achievements INNER JOIN Users_Achievements ON Users_Achievements.Achievement_ID = Achievements.ID \
            WHERE Users_Achievements.User_ID = ? \
            ORDER BY Users_Achievements.Number DESC;", (self.UserID,))
            
            for _ in cursor:
                _returnValue.append({
                    "ID" :_[0], 
                    "Name" : _[1],
                    "Description" : _[2],
                    "Current" : _[3],
                    "Target" :_[4]})

            #Get the rest of the Achievements
            cursor.execute("SELECT ID, Name, Description, Target \
            FROM Achievements;")

            for _ in cursor:
                _returnValue.append({
                    "ID" :_[0], 
                    "Name" : _[1],
                    "Description" : _[2],
                    "Current" : 0,
                    "Target" :_[3]})

            return _returnValue


    def addVisitedLocation(self, requestBody):
        if(self.UserID >= 0):
            try:
                #ID, City, LocationName, Stars, NrReviews
                cursor = self.cursor
                if (int(requestBody["NrReviews"]) == 0):
                    calculatedScore = 1
                else:
                    calculatedScore = (int(requestBody["NrReviews"]) // float(6-float(requestBody["Stars"]))) 
                cursor.execute("INSERT INTO Travel_Log \
                    (User_ID, Country, Location_ID, City, Location, Score) VALUES \
                    (?, ?, ?, ?, ?, ?)", (self.UserID, requestBody["Country"], requestBody["ID"], \
                        requestBody["City"], requestBody["LocationName"], calculatedScore))


                self.conn.commit()        
                #Find achievement with given country, it might be a list

                cursor.execute("SELECT ID FROM Achievements \
                WHERE Country = ?;", (requestBody["Country"],))

                response = cursor.fetchone()
                
                #Update Users_Achievements ++ 
                if(response == None):
                    return
                updateArray = []
                for _ in cursor:
                    updateArray.append(_[0]) #achievemnts id, and cound

                for _ in updateArray:
                    cursor.execute("INSERT IGNORE INTO Users_Achievements \
                    (User_ID, Achievement_ID) VALUES (?, ?)", (self.UserID, _,))

                self.conn.commit()                

                #Now update users
                for _ in updateArray:
                    cursor.execute("UPDATE Users_Achievements SET Number = Number + 1\
                        WHERE User_ID = ? and Achievement_ID = ?;", (self.UserID, _,))

                self.conn.commit()                

            except mariadb.Error as e:
                self.conn.rollback()
                raise DBException('Error while inserting visited locaiton!')
        else:
            raise DBException('No user is logged int! Break!')


    def isVisited(self, LocationID):
        if(self.UserID >= 0):
            try:
                cursor = self.cursor
                cursor.execute("SELECT Location FROM Travel_Log \
                    WHERE User_ID = ? and Location_ID = ?;", (self.UserID, LocationID,))
                response = cursor.fetchone()
                if(response == None):
                    return None
                else:
                    return response[0]

            except Exception as e:
                return None
        return None


    def getLeaderBoard(self, country):
        if(self.UserID >= 0):
            try:
                
                if(country == ""):
                    return None

                cursor = self.cursor

                cursor.execute("SELECT Users.Username, SUM(Score) as ScoreSum FROM Travel_Log \
                    INNER JOIN Users ON Travel_Log.User_ID = Users.ID \
                    WHERE Travel_Log.City RLIKE '" + country + ".' or Travel_Log.City = ? GROUP BY Users.Username \
                    Order BY ScoreSum DESC;", (country,))

                retrievedData = []
                for _ in cursor:
                    retrievedData.append({
                        "UserName" : _[0],
                        "Score" : float(_[1])
                    })
                return retrievedData

            except mariadb.Error as e:
                self.conn.rollback()
                raise DBException('Error while inserting visited locaiton!')


    

class DBException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.errors = message

    def print(self): #define JSON for exception Here
        _returnValue = {
            "statusCode" : 500,
            "message" : self.errors
        }
        return _returnValue    



