# %%
import pandas as pd

# Tool for avoiding format issues
import datetime as dt
from datetime import datetime, timedelta

# Tool for building a database in Python
import sqlite3

# Tool for a simple CLI
from tabulate import tabulate

# Exit for the program
import sys

# support for regular expressions
import random

# %%
# Create Connection to Database
conn = sqlite3.connect("habit_tracker.db")
cursor = conn.cursor()

# Entity 1: calendar
cursor.execute("""drop table calendar""")
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS calendar (
        date DATE PRIMARY KEY
    )
"""
)
# Automatically filling in the dates for one year
start_date = datetime(2023, 1, 1)
end_date = start_date + timedelta(days=365)

for day in range((end_date - start_date).days + 1):
    current_date = start_date + timedelta(days=day)
    cursor.execute("INSERT INTO calendar (date) VALUES (?)", (current_date.date(),))

# Entitity 2: habit
cursor.execute("""drop table habit""")
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS habit (
        idhabit INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_name VARCHAR,
        habit_interval INT,
        timestamp_creation TIMESTAMP
    )
"""
)
# Automatically filling in five predefined habits in the entity habit
habits_data = [
    ("Walking", 1),
    ("Workout", 2),
    ("Meditation", 3),
    ("Hiking", 7),
    ("Read book", 30),
]

for habit_name, habit_interval in habits_data:
    cursor.execute(
        "INSERT INTO habit (habit_name, habit_interval) VALUES (?, ?)",
        (habit_name, habit_interval),
    )

# Relationship-Entity
cursor.execute("""drop table calendar_has_habit""")
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS calendar_has_habit (
        timestamp VARCHAR PRIMARY KEY,
        idhabit INT,
        idcalendar DATE,
        FOREIGN KEY (idcalendar) REFERENCES calendar (idcalendar) ON DELETE CASCADE,
        FOREIGN KEY (idhabit) REFERENCES habit (idhabit) ON DELETE CASCADE
    )
"""
)


conn.commit()
conn.close()

# %%
# enter random data

habits_data = [
    ("Walking", 1, 35),
    ("Workout", 2, 20),
    ("Meditation", 3, 18),
    ("Hiking", 7, 4),
    ("Read book", 30, 2),
]
time_delta = 0
for habit in habits_data:
    time_delta += 1

    # Create Connection to Database
    conn = sqlite3.connect("habit_tracker.db")
    cursor = conn.cursor()

    start_date = "2023-11-01"
    end_date = "2023-12-31"

    n = habit[2]

    date_range = pd.date_range(start=start_date, end=end_date)
    sampled_date_range = random.sample(list(date_range), n)
    sampled_date_range.sort()

    for date in sampled_date_range:
        # Insert data into the relationship table using habit_id
        track_habit = f"""INSERT INTO calendar_has_habit(timestamp, idhabit, idcalendar) 
        VALUES (?, (SELECT idhabit FROM habit WHERE habit_name = ?), ?)"""
        cursor.execute(
            track_habit,
            (str(date + dt.timedelta(hours=time_delta)), habit[0], date.date()),
        )

    conn.commit()
    conn.close()

# %%
# create the longest streak, which will be walking

# Create Connection to Database
conn = sqlite3.connect("habit_tracker.db")
cursor = conn.cursor()

start_date = "2023-11-01"
end_date = "2023-11-14"


date_range = pd.date_range(start=start_date, end=end_date)

for date in date_range:
    # Insert data into the relationship table using habit_id
    track_habit = f"""INSERT OR IGNORE INTO calendar_has_habit(timestamp, idhabit, idcalendar) 
    VALUES (?, (SELECT idhabit FROM habit WHERE habit_name = ?), ?)"""
    cursor.execute(
        track_habit, (str(date + dt.timedelta(hours=1)), "Walking", date.date())
    )


conn.commit()
conn.close()


print("Your test data has been created")
