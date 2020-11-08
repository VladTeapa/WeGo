CREATE TABLE IF NOT EXISTS Users (
    ID INT NOT NULL AUTO_INCREMENT,
    OauthID VARCHAR(255),
    Username VARCHAR(255) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL,
    PRIMARY KEY (ID)
);

CREATE TABLE IF NOT EXISTS Achievements (
    ID INT NOT NULL AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Description VARCHAR(255) NOT NULL,
    Country VARCHAR(255),
    Category VARCHAR(255),
    Landmark VARCHAR(255),
    Target INT NOT NULL DEFAULT 7,
    PRIMARY KEY (ID)
);

CREATE TABLE IF NOT EXISTS Users_Achievements (
    ID INT NOT NULL AUTO_INCREMENT,
    User_ID INT NOT NULL,
    Achievement_ID INT NOT NULL,
    Number INT NOT NULL DEFAULT 0,
    PRIMARY KEY (ID),
    FOREIGN KEY (User_ID) REFERENCES Users (ID) ON DELETE CASCADE,
    FOREIGN KEY (Achievement_ID) REFERENCES Achievements (ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Travel_Log (
    ID INT NOT NULL AUTO_INCREMENT,
    User_ID INT NOT NULL,
    Location_ID VARCHAR(255),
    Country VARCHAR(255),
    City VARCHAR(255),
    Location VARCHAR(255),
    Date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Score INT NOT NULL,
    PRIMARY KEY (ID),
    FOREIGN KEY (User_ID) REFERENCES Users (ID) ON DELETE CASCADE
);
