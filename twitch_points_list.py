import csv

import pandas as pd
from datetime import datetime


class TwitchPointsList:
    streamers = []

    def __init__(self):
        pass

    def add_entry(self, streamer):
        if streamer not in self.streamers:
            self.streamers.append(streamer)
        else:
            # Add points and date to the streamer
            self.streamers[self.streamers.index(streamer)].add_entry(streamer.points[-1], streamer.dates[-1])

    def remove_entry(self, streamer):
        self.streamers.remove(streamer)

    def get_entry(self, name):
        for streamer in self.streamers:
            if streamer.name == name:
                return streamer
        return None

    def __str__(self):
        return str(self.streamers)

    def save_to_file(self, filename):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for streamer in self.streamers:
                for i in range(len(streamer.points)):
                    writer.writerow([streamer.name, streamer.points[i], streamer.dates[i], streamer.target])

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                date = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S.%f")
                if len(row) == 4:
                    self.add_entry(Streamer(row[0], int(row[1]), date, int(row[3])))
                else:
                    self.add_entry(Streamer(row[0], int(row[1]), date))

    def to_df(self):
        """
        Convert the list of streamers to a Pandas DataFrame.

        Returns:
        - pd.DataFrame: DataFrame containing streamer data.
        """
        data = []
        for streamer in self.streamers:
            percentage = streamer.points[-1] / streamer.target * 100 if streamer.target is not None else None
            data.append([streamer, streamer.name, streamer.points[-1], streamer.target, percentage, str(streamer.est_date)])

        # Define column names
        columns = ["streamer_object", "name", "points", "target", "percentage", "est_date"]

        # Define data types for each column
        # dtypes = {"Name": str, "Points": int, "Target": int, "Est. Date": str}

        # Create DataFrame with specified data types
        df = pd.DataFrame(data, columns=columns)

        return df


class Streamer:
    est_date = None

    def __init__(self, name, points, date, target=None):
        self.name = name
        self.points = [points]
        self.dates = [date]
        self.target = target

    def add_entry(self, points, date):
        self.points.append(points)
        self.dates.append(date)

    def edit(self, points=None, target=None):
        if points is not None:
            self.add_entry(points, str(datetime.now()))
        if target is not None:
            self.target = target

    def __str__(self):
        return str(self.name) + " " + str(self.points) + " " + str(self.dates) + " " + str(self.target)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
