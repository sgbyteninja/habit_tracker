import sqlite3
import datetime as dt
import pytest
from Habit_Tracker import Connector, Analyzer, Error_Handling


# Testing creating a new habit
def test_insert_habit(monkeypatch):
    # Simulate user inputs
    habit_name_input = "Test"
    habit_interval_input = "1"

    # Create an instance of Connector
    connector = Connector("habit_tracker.db")
    analyzer_instance = Analyzer()

    # Simulate input for habit_name
    monkeypatch.setattr("builtins.input", lambda _: habit_name_input)

    # Simulat input for habit_interval
    monkeypatch.setattr("builtins.input", lambda _: habit_interval_input)

    # Call the insert function
    connector.insert(habit_name_input, habit_interval_input)

    test_df = analyzer_instance.get_all_habits()

    assert ("Test" in list(test_df.habit_name)) == True


# Testing seeing a list of all habits with the same interval
def test_get_same_interval(monkeypatch):
    # Simulate user input
    interval_input = "1"

    # Create an instance of Connector
    analyzer_instance = Analyzer()

    # Simulate user input for interval
    monkeypatch.setattr("builtins.input", lambda _: interval_input)

    # Call get_same_interval function
    test_df = analyzer_instance.get_same_interval(interval_input)

    # Check if the habits are in the resulting DataFrame
    assert (
        all(habit in test_df.habit_name.tolist() for habit in ["Walking", "Test"])
        == True
    )


# Testing updating a habit
def test_update(monkeypatch):
    # Simulate user input
    habit_name_input = "Test"
    new_habit_name_input = "New"

    # Create instance of Connector
    connector_instance = Connector("habit_tracker.db")
    analyzer_instance = Analyzer()

    # Simulate input for habit_name
    monkeypatch.setattr("builtins.input", lambda _: habit_name_input)

    # Simulat input for habit_interval
    monkeypatch.setattr("builtins.input", lambda _: new_habit_name_input)

    # Call update function
    connector_instance.update(habit_name_input, new_habit_name_input)

    test_df = analyzer_instance.get_all_habits()

    assert ("New" in list(test_df.habit_name)) == True


# Testing deleting a habit
def test_delete_habit(monkeypatch):
    # Simulate user input
    habit_name_input = "New"

    # Create an instance of Connector
    connector_instance = Connector("habit_tracker.db")
    analyzer_instance = Analyzer()

    # Simulate input for habit_name
    monkeypatch.setattr("builtins.input", lambda _: habit_name_input)

    # Call delete function
    connector_instance.delete(habit_name_input)

    test_df = analyzer_instance.get_all_habits()

    assert ("New" in list(test_df.habit_name)) == False


# Testing tracking a habit
def test_track_habit(monkeypatch):
    # Simulate user input
    habit_name_input = "Hiking"

    # Create an instance of Connector
    connector_instance = Connector("habit_tracker.db")
    analyzer_instance = Analyzer()

    # Simulate input for habit_name
    monkeypatch.setattr("builtins.input", lambda _: habit_name_input)

    idcalendar = dt.datetime.now().strftime("%Y-%m-%d")
    # Call tracking function
    connector_instance.track(habit_name_input)
    test_df = analyzer_instance.get_tracking_entries(habit_name_input)
    assert (idcalendar in list(test_df.idcalendar)) == True


# Testing deleting the tracking entry
def test_delete_tracking_entry_today(monkeypatch):
    # Simulate user input
    habit_name_input = "Hiking"

    # Create an instance of Connector
    connector_instance = Connector("habit_tracker.db")
    analyzer_instance = Analyzer()

    # Simulate input for habit_name
    monkeypatch.setattr("builtins.input", lambda _: habit_name_input)
    idcalendar = dt.datetime.now().strftime("%Y-%m-%d")

    # Call function for deleting tracking entries
    connector_instance.delete_tracking_entry(habit_name_input, idcalendar)
    test_df = analyzer_instance.get_tracking_entries(habit_name_input)
    assert (idcalendar in list(test_df.idcalendar)) == False


# Testing tracking on an other day
def test_track_different_date(monkeypatch):
    # Simulate user input
    habit_name_input = "Hiking"
    id_calendar_input = "2023-12-12"

    # Create an instance of Connector
    connector_instance = Connector("habit_tracker.db")
    analyzer_instance = Analyzer()

    # Simulate input for habit_name
    monkeypatch.setattr("builtins.input", lambda _: habit_name_input)

    # Simulate input for date
    monkeypatch.setattr("builtins.input", lambda _: id_calendar_input)

    # Call tracking function
    connector_instance.track_different_date(id_calendar_input, habit_name_input)
    test_df = analyzer_instance.get_tracking_entries(habit_name_input)
    assert (id_calendar_input in list(test_df.idcalendar)) == True


# Testing deleting the tracking entry
def test_delete_tracking_entry_other_day(monkeypatch):
    # Simulate user input
    habit_name_input = "Hiking"
    idcalendar_input = "2023-12-12"

    # Create an instance of Connector
    connector_instance = Connector("habit_tracker.db")
    analyzer_instance = Analyzer()

    # Simulate input for habit_name
    monkeypatch.setattr("builtins.input", lambda _: habit_name_input)
    monkeypatch.setattr("builtins.input", lambda _: idcalendar_input)

    # Call function for deleting tracking entries
    connector_instance.delete_tracking_entry(habit_name_input, idcalendar_input)
    test_df = analyzer_instance.get_tracking_entries(habit_name_input)
    assert (idcalendar_input in list(test_df.idcalendar)) == False


# Testing analyzing current streak of a habit
def test_analyze_current_streak(monkeypatch):
    # Simulate user input for habit_name
    habit_name_input = "Walking"

    # Create instance of Analyzer
    analyzer_instance = Analyzer()

    # Simulate input for habit_name
    monkeypatch.setattr("builtins.input", lambda _: habit_name_input)

    # Call analyze current streak of a habit function
    current_streak_length = analyzer_instance.analyze_streak_for_habit(
        habit_name_input
    )[0]

    assert (current_streak_length == 2) == True


# Testing analyzing current streak of a habit
def test_analyze_longest_streak(monkeypatch):
    # Simulate user input for habit_name
    habit_name_input = "Workout"

    # Create instance of Analyzer
    analyzer_instance = Analyzer()

    # Simulate input for habit_name
    monkeypatch.setattr("builtins.input", lambda _: habit_name_input)

    # Call analyze current streak of a habit function
    longest_streak_length = analyzer_instance.analyze_streak_for_habit(
        habit_name_input
    )[3]

    assert (longest_streak_length == 4) == True


def test_longest_streak_all_habits():
    # Create instance of Analyzer
    analyzer_instance = Analyzer()

    # Call analyze longest streak of all habits function
    (
        habit_longest_streak,
        overall_longest_streak_habit,
    ) = analyzer_instance.analyze_longest_streak_all_habits()

    # Assert that the overall longest streak habit is "walking" with a length of 14
    assert (overall_longest_streak_habit == "Walking") == True


# Testing seeing a list of all tracked habits
def test_get_all_habits():
    # Create an instance of Analyzer
    analyzer_instance = Analyzer()
    connector_instance = Connector("habit_tracker.db")
    # Call function for seeing all stored habits
    test_df = analyzer_instance.get_all_habits()
    print(test_df)
    assert (
        all(
            habit in test_df.habit_name.tolist()
            for habit in ["Walking", "Read book", "Hiking", "Meditation", "Workout"]
        )
        == True
    )

    # Testing getting a list of all tracking entries of a habit


def test_get_tracking_entries(monkeypatch):
    # Simulate user input for habit_name
    habit_name_input = "Hiking"

    # Create instance of Connector
    analyzer_instance = Analyzer()

    # Simulate input for habit_name
    monkeypatch.setattr("builtins.input", lambda _: habit_name_input)

    # Call function to get tracking entries
    test_df = analyzer_instance.get_tracking_entries(habit_name_input)

    assert (len(test_df) == 4) == True


# Testing getting the interval for a habit
def test_get_interval(monkeypatch):
    habit_name_input = "Walking"

    # Create an instance of Connector
    analyzer_instance = Analyzer()

    # Simulate input for habit_name
    monkeypatch.setattr("builtins.input", lambda _: habit_name_input)

    # Call get interval function
    habit_interval = analyzer_instance.get_interval(habit_name_input)

    assert habit_interval == 1


# Testing if account exists
def test_account_exists():
    # Create an instance of Error_Handling
    error_handling_instance = Error_Handling()

    # Call account exits function
    result = error_handling_instance.account_exists()
    assert result == True


# Testing check if habit exists
def test_habit_exists(monkeypatch):
    # Simulate user input for existing habit
    habit_name_input1 = "Walking"

    # Create an instance of Error_Handling
    error_handling_instance = Error_Handling()

    # Simulate input for habit_name
    monkeypatch.setattr("builtins.input", lambda _: habit_name_input1)

    # Call habit_exists function with the habit_name argument
    result = error_handling_instance.habit_exists(habit_name_input1)
    assert result == True

    # Simulate user input for non existing habit
    habit_name_input2 = "Dancing"

    # Create an instance of Error_Handling
    error_handling_instance = Error_Handling()

    # Simulate input for habit_name
    monkeypatch.setattr("builtins.input", lambda _: habit_name_input2)

    # Call habit_exists function with the habit_name argument
    result = error_handling_instance.habit_exists(habit_name_input2)
    assert result == False


# Testing check if there are two entries for one day
def test_entry_checker():
    # Simulate user input for entry that already exists
    habit_name_input = "Walking"
    date_input1 = "2023-12-20"
    specific_date_obj = dt.datetime.strptime(date_input1, "%Y-%m-%d")

    # Create an instance of Connector
    error_handling_instance = Error_Handling()

    # Call entry checker function
    assert (
        error_handling_instance.entry_checker(
            specific_date_obj.date(), habit_name_input
        )
    ) == True

    # Simulate user input for entry that doesn't already exist
    habit_name_input = "Walking"
    date_input2 = "2023-12-17"
    specific_date_obj2 = dt.datetime.strptime(date_input2, "%Y-%m-%d")

    # Create an instance of Connector
    error_handling_instance = Error_Handling()

    # Call entry checker function
    assert (
        error_handling_instance.entry_checker(
            specific_date_obj2.date(), habit_name_input
        )
    ) == False


# Testing check if user input is in range
def test_date_checker():
    # Simulate user input for date that exists
    date1 = "2023-12-10"
    specific_date_obj1 = dt.datetime.strptime(date1, "%Y-%m-%d")

    # Create instance of Error_Handling
    error_handling_instance = Error_Handling()

    # Call date_checker function
    result1 = error_handling_instance.date_checker(specific_date_obj1.date())
    assert result1 is False

    # Simulate user input for date that doesn't exist
    date2 = "2005-01-01"
    specific_date_obj2 = dt.datetime.strptime(date2, "%Y-%m-%d")

    # Create instance of Error_Handling
    error_handling_instance = Error_Handling()

    # Call date_checker function
    result2 = error_handling_instance.date_checker(specific_date_obj2.date())
    assert result2 is True
