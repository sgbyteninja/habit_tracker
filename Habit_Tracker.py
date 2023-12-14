# # Packages
import pandas as pd

# Tool for avoiding format issues, please save me python god.
import datetime as dt
from datetime import datetime, timedelta

# Tool for building a database in Python
import sqlite3

# Tool for a simple CLI
from tabulate import tabulate

# Exit for the program
import sys


# Class Connector
class Connector:
    def __init__(self, database):
        self.database = database

    def initial_startup(self):
        # Create Connection to Database
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        # Entity 1: calendar
        cursor.execute("""DROP TABLE IF EXISTS calendar""")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS calendar (
                date DATE PRIMARY KEY
            )
        """
        )
        # Automatically filling in the dates for one year
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=365)

        current_date = start_date
        while current_date <= end_date:
            cursor.execute("INSERT INTO calendar (date) VALUES (?)", (current_date,))
            current_date += timedelta(days=1)

        # Entity 2: habit
        cursor.execute("""DROP TABLE IF EXISTS habit""")
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

        # Entity 3: Relationship Table
        cursor.execute("""DROP TABLE IF EXISTS calendar_has_habit""")
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

    # a function that will trigger if one year after initial start up expires
    def one_year_has_passed(self):
        try:
            df = analyzer.get_all_calendar()

            # it will fill 365 new entries into the calender, and if the current date is not within the calender
            # it will fill up with the while loop until the current date.
            while (
                str(dt.date.today()) in list(analyzer.get_all_calendar().date)
            ) == False:
                conn = sqlite3.connect(database=connector.database)
                cursor = conn.cursor()
                date_string = df.date.loc[365]

                date_object = dt.datetime.strptime(date_string, "%Y-%m-%d")
                start_date = date_object.date() + timedelta(days=1)
                end_date = start_date + timedelta(days=365)

                current_date = start_date

                while current_date <= end_date:
                    cursor.execute(
                        "INSERT INTO calendar (date) VALUES (?)", (current_date,)
                    )
                    current_date += timedelta(days=1)

                conn.commit()
                cursor.close()
                conn.close()
                # this will update the calendar so that the loop breaks
                df = analyzer.get_all_calendar()
                df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
        except sqlite3.Error as e:
            print(e)

    # INSERT Statements to create new habits
    def insert(self, habit_name, habit_interval):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            timestamp_creation = dt.datetime.now()
            insert_query = """
            INSERT INTO habit (habit_name, habit_interval, timestamp_creation)
            VALUES (?, ?, ?)
            """
            data = (habit_name, int(habit_interval), timestamp_creation)
            cursor.execute(insert_query, data)
            conn.commit()
        except sqlite3.Error as e:
            print(e)

            # Check if the connection object exists before closing
            if "conn" in locals() and conn is not None:
                cursor.close()
                conn.close()

    # INSERT Statement to track a habit
    def track(self, habit_name):
        try:
            conn = sqlite3.connect(database=self.database)
            cursor = conn.cursor()

            # Automatically fill in current timestamp
            current_datetime = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Automatically fill in current date
            current_date = dt.datetime.now().strftime("%Y-%m-%d")

            # SELECT Statement to get the habit-id of the entered habit
            get_habit_id_query = (
                f"""SELECT idhabit FROM habit WHERE (habit_name) = ('{habit_name}')"""
            )
            cursor.execute(get_habit_id_query)
            habit_id_result = cursor.fetchone()

            habit_idhabit = int(habit_id_result[0])

            # Insert data into the relationship table using habit_id
            track_habit = f"""INSERT INTO calendar_has_habit(idcalendar, idhabit, timestamp) 
            VALUES ('{current_date}', '{habit_idhabit}', '{current_datetime}')"""
            cursor.execute(track_habit)
            conn.commit()
            print(f"You have successfully tracked the habit '{habit_name.title()}'.")

        except sqlite3.Error as e:
            print("Error:", e)
        finally:
            # Close the cursor and connection
            if "conn" in locals() and conn is not None:
                cursor.close()
                conn.close()

    # Delete tracking entry
    def delete_tracking_entry(self, habit_name, date):
        try:
            conn = sqlite3.connect(database=self.database)
            cursor = conn.cursor()

            # SELECT Statement to get the habit-id of the entered habit
            get_habit_id_query = (
                f"""SELECT idhabit FROM habit WHERE (habit_name) = ('{habit_name}')"""
            )
            cursor.execute(get_habit_id_query)
            habit_id_result = cursor.fetchone()

            habit_idhabit = int(habit_id_result[0])

            # DELETE Statement to remove the specific tracked habit entry
            delete_entry_query = f"""DELETE FROM calendar_has_habit 
                                         WHERE idhabit = {habit_idhabit} AND idcalendar = '{date}'"""
            cursor.execute(delete_entry_query)
            conn.commit()

        except sqlite3.Error as e:
            print("Error:", e)
        finally:
            # Close the cursor and connection
            if "conn" in locals() and conn is not None:
                cursor.close()
                conn.close()

    # Track habit on an other day
    def track_different_date(self, idcalendar, habit_name):
        try:
            conn = sqlite3.connect(database=self.database)
            cursor = conn.cursor()

            # Input current time
            current_datetime = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # SELECT Statement to get the habit-id of the entered habit
            get_habit_id_query = (
                f"""SELECT idhabit FROM habit WHERE habit_name = '{habit_name}'"""
            )
            cursor.execute(get_habit_id_query)
            habit_id_result = cursor.fetchone()

            # Check if habit exists
            if habit_id_result is not None and habit_id_result[0] is not None:
                habit_idhabit = int(habit_id_result[0])

                # Insert data into the relationship table using habit_id
                track_habit = f"""INSERT INTO calendar_has_habit(idcalendar, idhabit, timestamp) 
                VALUES ('{idcalendar}', '{habit_idhabit}', '{current_datetime}')"""
                cursor.execute(track_habit)
                conn.commit()
                print(
                    f"You have successfully tracked the habit '{habit_name.title()}' on the date {idcalendar}."
                )
            else:
                print(f"No habit found with the name '{habit_name.title()}'")

        except sqlite3.Error as e:
            print("Error:", e)
        finally:
            # Close the cursor and connection
            if "conn" in locals() and conn is not None:
                cursor.close()
                conn.close()

    # DELETE Statements to delete habits
    def delete(self, habit_name):
        try:
            conn = sqlite3.connect(database=self.database)
            cursor = conn.cursor()
            delete_statement = (
                f"""DELETE FROM habit WHERE habit_name = '{habit_name}'"""
            )
            cursor.execute(delete_statement)
            conn.commit()
        except sqlite3.connect.Error as e:
            print(e)
        finally:
            if "conn" in locals() and conn is not None:
                cursor.close()
                conn.close()

    # UPDATE Statements to change habit
    def update(self, habit_name, new_habit_name):
        try:
            conn = sqlite3.connect(database=self.database)
            cursor = conn.cursor()
            update_statement = f"""UPDATE habit SET habit_name = '{new_habit_name}' WHERE habit_name = '{habit_name}'"""
            cursor.execute(update_statement)
            conn.commit()
        except sqlite3.Error as e:
            print(e)
        finally:
            if "conn" in locals() and conn is not None:
                cursor.close()
                conn.close()


# Class Analyzer
class Analyzer:
    def __init__(self):
        pass

    # SELECT Statements to see calendar-entries
    def get_all_calendar(self):
        try:
            conn = sqlite3.connect(database=connector.database)
            cursor = conn.cursor()
            get_all_statement = f"""SELECT * FROM calendar"""
            cursor.execute(get_all_statement)
            results = cursor.fetchall()
            columns = [i[0] for i in cursor.description]

            # Create DataFrame
            df = pd.DataFrame(results, columns=columns)
            cursor.close()
            conn.close()
            return df
        except sqlite3.Error as e:
            print(e)

    # Get a list of all tracked habits
    def get_all_habits(self):
        try:
            conn = sqlite3.connect(database=connector.database)
            cursor = conn.cursor()
            get_all_habits = f"""SELECT habit_name FROM habit"""
            cursor.execute(get_all_habits)
            results = cursor.fetchall()
            columns = [i[0] for i in cursor.description]

            # Create DataFrame
            df = pd.DataFrame(results, columns=columns)
            cursor.close()
            conn.close()
            return df
        except sqlite3.Error as e:
            print(e)

    # Get a list of all habits with the same interval
    def get_same_interval(self, interval):
        try:
            conn = sqlite3.connect(database=connector.database)
            cursor = conn.cursor()
            get_same_interval = (
                f"""SELECT habit_name FROM habit WHERE habit_interval = {interval}"""
            )
            cursor.execute(get_same_interval)
            results = cursor.fetchall()

            # Check if there are results
            if results:
                columns = ["habit_name"]
                df = pd.DataFrame(results, columns=columns)
                cursor.close()
                conn.close()
                return df
            else:
                print(f"No habits found with the interval {interval}")
                # Return empty DataFrame
                return pd.DataFrame()
        except sqlite3.Error as e:
            print(e)
            return pd.DataFrame()

    # Get the interval of a habit
    def get_interval(self, habit_name):
        try:
            conn = sqlite3.connect(connector.database)
            cursor = conn.cursor()
            get_interval = (
                f"""SELECT habit_interval FROM habit WHERE habit_name='{habit_name}'"""
            )
            cursor.execute(get_interval)
            results = cursor.fetchall()
            columns = [i[0] for i in cursor.description]

            # Create DataFrame
            df = pd.DataFrame(results, columns=columns)
            cursor.close()
            conn.close()
            return df.loc[0]["habit_interval"]

        except sqlite3.Error as e:
            print(e)
        finally:
            if conn is None:
                cursor.close()
                conn.close

    # Get a list of all tracking entries of a habit
    def get_tracking_entries(self, habit_name):
        try:
            conn = sqlite3.connect(connector.database)
            cursor = conn.cursor()
            get_tracking_entries = f""" SELECT habit_name, idcalendar, timestamp FROM calendar_has_habit INNER JOIN habit ON calendar_has_habit.idhabit=habit.idhabit WHERE habit_name = '{habit_name}'"""
            cursor.execute(get_tracking_entries)
            results = cursor.fetchall()
            columns = [i[0] for i in cursor.description]

            # Create DataFrame
            df = pd.DataFrame(results, columns=columns)
            cursor.close()
            conn.close()
            return df
        except sqlite3.Error as e:
            print(e)

    # Analyse maximum and current streak length of a habit
    def analyze_streak_for_habit(self, habit_name):
        # Get habit interval
        habit_interval = analyzer.get_interval(habit_name)

        # Get tracking entries
        habit_df = analyzer.get_tracking_entries(habit_name)

        # Check if df is empty
        if habit_df.empty:
            # print(f"No tracking entries found for habit '{habit_name}'.")
            return 0, None, None, 0, None, None

        # Ensure correct format
        habit_df.idcalendar = pd.to_datetime(habit_df.idcalendar, format="%Y-%m-%d")

        # Sort DataFrame by timestamp
        habit_df.sort_values(by="idcalendar", inplace=True)
        current_streak_length = 1
        max_streak_length = 1
        max_streak_start = habit_df.iloc[0]["idcalendar"]
        max_streak_end = habit_df.iloc[0]["idcalendar"]
        current_streak_start = habit_df.iloc[0]["idcalendar"]
        current_streak_end = habit_df.iloc[0]["idcalendar"]

        # here is where the magic happens
        for i in range(1, len(habit_df)):
            time_diff = (
                habit_df.iloc[i]["idcalendar"] - habit_df.iloc[i - 1]["idcalendar"]
            )
            days_diff = time_diff.days

            if 1 <= days_diff <= habit_interval:
                current_streak_length += 1
                current_streak_end = habit_df.iloc[i]["idcalendar"]
            else:
                # Streak is broken, set streak length to  1
                current_streak_length = 1
                current_streak_start = habit_df.iloc[i]["idcalendar"]

            # Update max streak length
            if current_streak_length > max_streak_length:
                max_streak_length = current_streak_length
                max_streak_start = current_streak_start
                max_streak_end = current_streak_end

        return (
            current_streak_length - 1,
            current_streak_start,
            current_streak_end,
            max_streak_length - 1,
            max_streak_start,
            max_streak_end,
        )

    # Analyse longest streak of all habits
    def analyze_longest_streak_all_habits(self):
        # Create a list of all tracked habits
        habit_list = analyzer.get_all_habits()

        # Create empty dictionary to store longest streak for each habit
        habit_longest_streak = {}

        # Iterate through each habit
        for index, row in habit_list.iterrows():
            habit_name = row["habit_name"]
            # Analyze streak for the current habit
            (
                max_streak_length,
                max_streak_start,
                max_streak_end,
            ) = self.analyze_streak_for_habit(habit_name)[3:]

            # Store the longest streak for the current habit in the dictionary
            habit_longest_streak[habit_name] = {
                "length": max_streak_length,
                "start_date": max_streak_start.strftime("%Y-%m-%d")
                if max_streak_start is not None
                else None,
                "end_date": max_streak_end.strftime("%Y-%m-%d")
                if max_streak_end is not None
                else None,
            }

        # Identify the habit with the overall longest streak
        overall_longest_streak_habit = max(
            habit_longest_streak, key=lambda x: habit_longest_streak[x]["length"]
        )

        # return result
        return habit_longest_streak, overall_longest_streak_habit


# a class that will handle user input
class Error_Handling:
    def __init__(self):
        pass

    # check if there are entries in the calendar, so to warn the user, they might overwrite an existing database
    def account_exists(self):
        conn = sqlite3.connect(connector.database)
        cursor = conn.cursor()

        # Check if there is any data in the entity 'calendar'
        cursor.execute("SELECT COUNT(*) FROM calendar")
        count = cursor.fetchone()[0]

        conn.close()

        # If there is at least one entry in the entity 'calendar', an account is considered to exist
        return count > 0

    # check if there are two entries for one day, so no retracking happens
    def entry_checker(self, date, habit_name):
        tracking_df = analyzer.get_tracking_entries(habit_name)
        tracking_df["idcalendar"] = pd.to_datetime(tracking_df["idcalendar"])
        if (date in tracking_df["idcalendar"].dt.date.values) == True:
            return True
        else:
            return False

    # check if user input date is within tracking period
    def date_checker(self, idcalendar):
        try:
            conn = sqlite3.connect(database=connector.database)
            cursor = conn.cursor()
            # idcalendar.replace(hour=0, minute=0, second=0)
            cursor.execute(
                "SELECT COUNT(*) FROM calendar WHERE date = ?", (idcalendar,)
            )
            date_exists = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            if date_exists == 0:
                return True
            else:
                return False

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False

    # Check if habit exists, so that tracking is possible
    def habit_exists(self, habit_name):
        habit_df = analyzer.get_all_habits()
        if habit_name not in habit_df["habit_name"].values:
            return False
        else:
            return True


# Class Communicator
class Communicator:
    def __init__(self):
        self.welcomed = False

    # Welcome User
    def welcome(self):
        # a warm colorful hello, yet only once
        if not self.welcomed:
            print("\033[1;33m\t    HELLO, WELCOME TO YOUR HABIT TRACKER.\033[0m")
            self.welcomed = True

    # Show options of habit tracker
    def show_options(self):
        options = [
            ["1", "Create a new account"],
            ["2", "Create a new habit"],
            ["3", "Change an existing habit"],
            ["4", "Delete a habit"],
            ["5", "Get a list of all tracked habits"],
            ["6", "Get a list of all habits with the same interval"],
            ["7", "Track a habit"],
            ["8", "Track habit subsequently"],
            ["9", "Analyze the current streak of a habit"],
            ["10", "Analyze the longest streak of a habit"],
            ["11", "Analyze the longest streak of all habits"],
            ["12", "Show all entries for a habit"],
            ["13", "Delete a tracking entry for a habit"],
            ["0", "Exit"],
        ]
        # tabulate for the eye appealing interface
        print(
            tabulate(options, headers=["Option", "Description"], tablefmt="fancy_grid")
        )

    #
    def run(self):
        self.welcome()

        while True:
            self.show_options()
            user_input = input(
                "Enter the number of option you would like to choose (0-14): \n"
            )

            # Exit the program
            if user_input == "0":
                print("You are exiting the habit tracker. Goodbye! See you soon!")
                sys.exit()

            # Create new database
            elif user_input == "1":
                if error_handling.account_exists():
                    user_input = input(
                        "Are you sure you want to create a new account. Caution! An existing old one and all tracking data will be deleted. Answer Y or N: \n"
                    )
                    if user_input == "Y":
                        connector.initial_startup()
                    elif user_input == "N":
                        print("Canceled.")
                    else:
                        print("You have not provided the correct options.")
                else:
                    print("Account already exists. No need to create a new one.")
                self.run()

            # Create a new habit
            elif user_input == "2":
                habit_name = input(
                    "Enter the name of the habit you want to track."
                ).capitalize()

                # Check if habit already exists
                existing_habits = analyzer.get_all_habits()

                if habit_name in list(existing_habits.habit_name):
                    print(
                        f"Habit '{habit_name}' already exists. Please choose a different name."
                    )
                else:
                    habit_interval = input(
                        "Enter the interval of the habit you want to track: \n"
                    )
                    connector.insert(habit_name, habit_interval)
                    print(
                        f"Habit '{habit_name}' has been entered with an interval of {habit_interval}."
                    )

                self.run()

            # Change an existing habit
            elif user_input == "3":
                habit_name = input(
                    "Enter the habit name you want to change: \n"
                ).capitalize()
                new_habit_name = input(
                    "Enter the new name of the habit: \n"
                ).capitalize()
                connector.update(habit_name, new_habit_name)
                print(
                    f"You have successfully changed the the name of the habit from '{habit_name}' to '{new_habit_name}'."
                )
                self.run()

            # Delete an existing habit
            elif user_input == "4":
                habit_name = input(
                    "Enter the name of the habit you want to delete: \n"
                ).capitalize()
                connector.delete(habit_name)
                print(
                    f"You have successfully deleted the habit with the name '{habit_name}'."
                )
                self.run()

            # Get a list of all habits stored in the database
            elif user_input == "5":
                print("Here is a list of all habits, you have created.")
                habit_list = analyzer.get_all_habits()
                print(tabulate(habit_list, headers="keys", tablefmt="fancy_grid"))
                self.run()

            # Get a list of all habits with the same interval
            elif user_input == "6":
                interval = input(
                    "You want a list of all habits with the same interval? Then enter the desired interval: \n"
                )
                habit_list = analyzer.get_same_interval(interval)
                print(f"Here is a list of all habits with the interval {interval}.")
                print(tabulate(habit_list, headers="keys", tablefmt="fancy_grid"))
                self.run()

            # Track a habit
            elif user_input == "7":
                habit_name = input(
                    "Enter the name of the habit you want to track."
                ).capitalize()
                if error_handling.habit_exists(habit_name) == True:
                    # check if habit is already checked for today
                    current_date = datetime.now().date()
                    if error_handling.entry_checker(current_date, habit_name) == True:
                        print(
                            f"You have already tracked the habit '{habit_name}' today."
                        )
                    else:
                        connector.track(habit_name)
                else:
                    print(f"The habit with the name '{habit_name}' does not exist.")

                self.run()

            # Track habit on an other date
            elif user_input == "8":
                try:
                    specific_date = input(
                        "Enter the date for which you want to track your activity. Please make sure to give the date in the format YYYY-MM-DD: \n"
                    )
                    specific_date_obj = datetime.strptime(specific_date, "%Y-%m-%d")

                    habit_name = input(
                        "Enter the name of the habit you want to track: \n"
                    ).capitalize()

                    # check if entered date in tracking period
                    if error_handling.date_checker(specific_date_obj.date()) == True:
                        print(
                            f"Error: The specified date '{specific_date}' is outside your tracking period. You can only track habits after the creation date of your account."
                        )
                    # check if the habit was already tracked that day
                    elif error_handling.entry_checker(
                        specific_date_obj.date(), habit_name
                    ):
                        print(
                            f"You have already tracked the habit '{habit_name}' on {specific_date}."
                        )
                    else:
                        specific_date = specific_date_obj.date()
                        connector.track_different_date(
                            specific_date_obj.date(), habit_name
                        )

                except ValueError:
                    # If ValueError, the input is not in the expected format
                    print("You have not provided the right format.")

                self.run()

            # Analyze the current streak of a habit
            elif user_input == "9":
                habit_name = input(
                    "Enter the name of the habit for which you want to analyze the current streak: \n"
                ).capitalize()

                # Check if habit exists
                if error_handling.habit_exists(habit_name) == True:
                    current_streak = analyzer.analyze_streak_for_habit(habit_name)[0]
                    if current_streak == 0:
                        if len(analyzer.get_tracking_entries(habit_name)) == 0:
                            print(
                                f"No tracking entries found for habit '{habit_name}'."
                            )
                        elif len(analyzer.get_tracking_entries(habit_name)) != 0:
                            print(
                                f"You currently have no streak for you habit '{habit_name}'."
                            )
                    else:
                        print(
                            f"The current streak length of the habit '{habit_name}' is {current_streak}"
                        )

                else:
                    print(f"A habit with the name '{habit_name}' does not exist.")

                self.run()

            # Analyse longest streak of a habit
            elif user_input == "10":
                habit_name = input(
                    "Enter the name of the habit for which you want to analyze the longest streak: \n"
                ).capitalize()

                # Check if habit exists
                if error_handling.habit_exists(habit_name) == True:
                    result = analyzer.analyze_streak_for_habit(habit_name)
                    current_streak = result

                    max_streak_length, max_streak_start, max_streak_end = result[3:]
                    if max_streak_length > 0:
                        max_streak_start_str = max_streak_start.strftime("%Y-%m-%d")
                        max_streak_end_str = max_streak_end.strftime("%Y-%m-%d")
                        print(
                            f"The longest streak length of the habit '{habit_name}' is {max_streak_length}. It happened between the dates {max_streak_start_str} and {max_streak_end_str}."
                        )
                    else:
                        print(f"No tracking entries found for habit '{habit_name}'.")

                else:
                    print(f"A habit with the name '{habit_name}' does not exist.")

                self.run()

            # Analyse longest streak of all habits
            elif user_input == "11":
                (
                    habit_longest_streak,
                    overall_longest_streak_habit,
                ) = analyzer.analyze_longest_streak_all_habits()

                if overall_longest_streak_habit:
                    longest_streak_info = habit_longest_streak[
                        overall_longest_streak_habit
                    ]
                    print(
                        f"The habit with the overall longest streak is: {overall_longest_streak_habit} with a streak length of {longest_streak_info['length']}."
                    )

                    if (
                        longest_streak_info["start_date"] is not None
                        and longest_streak_info["end_date"] is not None
                    ):
                        print(
                            f"The streak occurred between the dates {longest_streak_info['start_date']} and {longest_streak_info['end_date']}."
                        )

                self.run()

            # See all tracking entries of a habit
            elif user_input == "12":
                habit_name = input(
                    "Enter the name of the habit for which you want to show your entries. \n"
                ).capitalize()
                df_entries = analyzer.get_tracking_entries(habit_name)
                print(
                    tabulate(
                        df_entries,
                        headers=["Habit Name", "Tracked Date", "System Timestamp"],
                        tablefmt="fancy_grid",
                        showindex=False,
                    )
                )

                self.run()

            # Delete a tracking entry
            elif user_input == "13":
                habit_name = input(
                    "Enter the name of the habit for which you want to delete a tracking_entry: \n"
                ).capitalize()

                # Check if habit exists
                if error_handling.habit_exists(habit_name) == True:
                    specific_date = input(
                        "Enter the date of the tracking entry you want to delete: \n"
                    )
                    try:
                        specific_date_obj = datetime.strptime(specific_date, "%Y-%m-%d")
                        if (
                            error_handling.entry_checker(
                                specific_date_obj.date(), habit_name
                            )
                            == True
                        ):
                            connector.delete_tracking_entry(habit_name, specific_date)
                            print(
                                f"You have successfully deleted the tracking entry on the date {specific_date} of the habit '{habit_name}"
                            )
                        else:
                            print(
                                f" No tracking entry on the date {specific_date} found for the habit '{habit_name}'"
                            )
                    except ValueError:
                        # If ValueError, the input is not in the expected format
                        print("You have not provided the right format.")
                else:
                    print(f"No habit found with the name '{habit_name}'")
                self.run()


communicator = Communicator()
# Innitialize Connector
connector = Connector("habit_tracker.db")
# Innitialize Analyzer
analyzer = Analyzer()
# Innitilaize error_handling
error_handling = Error_Handling()


if __name__ == "__main__":
    connector.one_year_has_passed()
    communicator.run()
