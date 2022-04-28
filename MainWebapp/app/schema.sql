CREATE TABLE ExternalWeather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_time_full TEXT,
    data_date_time TEXT,
    apparent_t FLOAT,
    true_t FLOAT,
    rel_hum INTEGER
);

CREATE TABLE InternalWeather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_date_time TEXT,
    true_t FLOAT,
    rel_hum INTEGER
);

CREATE TABLE Thresholds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    threshold FLOAT,
)