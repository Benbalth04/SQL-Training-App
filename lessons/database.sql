BEGIN TRANSACTION;

-- Recreate Countries table
DROP TABLE IF EXISTS Countries;
DROP TABLE IF EXISTS Cities;
DROP TABLE IF EXISTS People;

CREATE TABLE Countries (
    CountryID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Region TEXT NOT NULL,
    Population INTEGER NOT NULL
);

INSERT INTO Countries (Name, Region, Population) VALUES
    ('Australia', 'Oceania', 26000000),
    ('Canada', 'North America', 38000000),
    ('Japan', 'Asia', 125000000),
    ('Brazil', 'South America', 213000000),
    ('Germany', 'Europe', 83000000),
    ('Kenya', 'Africa', 54000000),
    ('New Zealand', 'Oceania', 5000000),
    ('India', 'Asia', 1380000000),
    ('United States', 'North America', 331000000),
    ('Argentina', 'South America', 45000000),
    ('Indonesia', 'Asia', 331000000);


CREATE TABLE Cities (
    CityID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    CountryID INTEGER NOT NULL,
    Population INTEGER,
    FOREIGN KEY (CountryID) REFERENCES Countries(CountryID)
);

INSERT INTO Cities (Name, CountryID, Population) VALUES
    ('Sydney', 1, 5300000),
    ('Melbourne', 1, 5100000),
    ('Toronto', 2, 2800000),
    ('Tokyo', 3, 14000000),
    ('Berlin', 5, 3600000),
    ('Nairobi', 6, 4300000),
    ('Auckland', 7, 1600000),
    ('Mumbai', 8, 20000000),
    ('New York', 9, 8400000),
    ('Jakarta', 9, 8400000),
    ('Sao Paulo', 4, 12300000);

CREATE TABLE People (
    PersonID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Age INTEGER NOT NULL,
    CountryID INTEGER,
    CityID INTEGER,
    FOREIGN KEY (CountryID) REFERENCES Countries(CountryID),
    FOREIGN KEY (CityID) REFERENCES Cities(CityID)
);

INSERT INTO People (Name, Age, CountryID, CityID) VALUES
    ('Alice', 29, 1, 1),
    ('Bob', 35, 1, 2),
    ('Carlos', 41, 4, 10),
    ('Diana', 22, 5, 5),
    ('Eva', 31, 3, 4),
    ('Frank', 27, 9, 9),
    ('Grace', 55, 2, 3),
    ('Hiro', 20, 3, 4),
    ('Isaac', 19, NULL, NULL), 
    ('Jamal', 44, 6, 6),
    ('Ben', 21, 11, NULL);

COMMIT;
