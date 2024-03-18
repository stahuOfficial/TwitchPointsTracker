from collections import deque

import joblib
import numpy as np

from twitch_points_list import TwitchPointsList
from sklearn.linear_model import LinearRegression
from datetime import datetime


def concatenate_data(dates, points):
    # Combine dates and points into tuples for easy sorting
    combined_data = list(zip(dates, points))
    # Sort combined data by dates in descending order
    combined_data.sort(reverse=True)

    # Use a deque to store unique dates
    unique_dates = deque(maxlen=30)
    result_dates = []
    result_points = []

    for date, point in combined_data:
        # Check if the date is not in the deque already
        if date.date() not in unique_dates:
            # Append the date and point to the result lists
            result_dates.append(date)
            result_points.append(point)
            # Append the date to the deque
            unique_dates.append(date.date())

        # Break the loop if we have already collected 30 unique dates
        if len(unique_dates) == 30:
            break

    # Reverse the lists to maintain the original order
    result_dates.reverse()
    result_points.reverse()

    return result_dates, result_points


class TwitchPointsModels:
    def __init__(self):
        self.twitch_points_list = TwitchPointsList()
        self.models: dict = {}

    def construct_model(self, streamer):
        dates, points = concatenate_data(streamer.dates, streamer.points)
        print(streamer.name)
        print(dates)
        print(points)

        timestamps = [date.timestamp() for date in dates]
        X = np.array(timestamps).reshape(-1, 1)
        y = np.array(points).reshape(-1, 1)

        model = LinearRegression()
        model.fit(X, y)

        self.models[streamer] = model

    def remove_model(self, streamer):
        self.models.pop(streamer)

    def save_models(self):
        joblib.dump(self.models, "models.pkl")

    def load_models(self):
        self.models = joblib.load("models.pkl")

    def predict(self, streamer, date):
        if len(streamer.dates) == 1:
            return datetime.max
        model = self.models[streamer]
        return model.predict([[date.timestamp()]])

    def when_target(self, streamer):
        if len(streamer.dates) == 1:
            return datetime.max
        model = self.models[streamer]
        w = model.coef_
        b = model.intercept_
        target = streamer.target
        return datetime.fromtimestamp(int((target - b) / w))
