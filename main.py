import os

from twitch_points_models import TwitchPointsModels
from twitch_points_list import TwitchPointsList
from gui.twitch_points_gui import TwitchPointsGUI


if __name__ == "__main__":
    print("Twitch Points Tracker")

    twitch_points = TwitchPointsList()
    if os.path.isfile("twitch_points.csv"):
        twitch_points.load_from_file("twitch_points.csv")
    else:
        twitch_points = TwitchPointsList()

    twitch_points_models = TwitchPointsModels()
    if os.path.isfile("models.pkl"):
        twitch_points_models.load_models()
    else:
        twitch_points_models = TwitchPointsModels()
    for streamer in twitch_points.streamers:
        if streamer not in twitch_points_models.models:
            twitch_points_models.construct_model(streamer)
    for streamer in twitch_points.streamers:
        streamer.est_date = twitch_points_models.when_target(streamer)

    TwitchPointsGUI(twitch_points, twitch_points_models)
