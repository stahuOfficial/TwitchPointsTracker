import joblib
import numpy as np

from twitch_points_list import TwitchPointsList
from sklearn.linear_model import LinearRegression
from datetime import datetime


def concatenate_data(dates, points):
    # Combine dates and points into tuples for easy sorting
    combined_data = list(zip(dates, points))

    # Get today's date
    today = datetime.now().date()

    # Initialize lists to store result
    result_dates = []
    result_points = []

    # Iterate over combined data
    for date, point in combined_data:
        # Calculate the difference in days between today and the date
        delta_days = (today - date.date()).days
        # If the difference is less than or equal to 30 days, include the data
        if delta_days <= 30:
            result_dates.append(date)
            result_points.append(point)

    return result_dates, result_points


class TwitchPointsModels:
    def __init__(self):
        self.twitch_points_list = TwitchPointsList()
        self.models: dict = {}

    def construct_model(self, streamer):
        dates, points = concatenate_data(streamer.dates, streamer.points)
        # dates, points = streamer.dates, streamer.points

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
