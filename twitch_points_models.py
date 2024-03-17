import joblib
import numpy as np

from twitch_points_list import TwitchPointsList
from sklearn.linear_model import LinearRegression
from datetime import datetime


# Return only the last entry on each day
def concatenate_data(dates, points):
    dates = sorted(dates)
    result_dates = [dates[0]]
    result_points = [points[0]]
    for i in range(1, len(dates)):
        if dates[i].date() != dates[i - 1].date():
            result_dates.append(dates[i])
            result_points.append(points[i])
        else:
            result_dates[-1] = dates[i]
            result_points[-1] = points[i]
    return result_dates, result_points


class TwitchPointsModels:
    def __init__(self):
        self.twitch_points_list = TwitchPointsList()
        self.models: dict = {}

    def construct_model(self, streamer):
        dates, points = concatenate_data(streamer.dates, streamer.points)
        # dates, points = streamer.dates, streamer.points
        print(streamer.name)
        print([date.strftime("%Y-%m-%d") for date in dates])
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
