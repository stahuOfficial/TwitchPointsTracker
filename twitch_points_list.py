import csv
import io

import numpy as np
import pandas as pd
from datetime import datetime

from matplotlib import pyplot as plt
from matplotlib import dates as mdates


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
            data.append(
                [streamer, streamer.name, streamer.points[-1], streamer.target, percentage, str(streamer.est_date)])

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

    def get_plot(self, model=None, height_px=450, background_color='#2b2b2b'):
        # Calculate the width based on the desired height and the aspect ratio (16:9)
        width_px = int(height_px * (16/9))

        # Convert width and height from pixels to inches
        width_in = width_px / 100
        height_in = height_px / 100

        # Format points labels
        formatted_points = [f"{point:,}".replace(",", " ") for point in self.points]

        # Create a dark-themed plot
        plt.style.use('dark_background')

        # Plotting
        fig, ax = plt.subplots(figsize=(width_in, height_in))
        ax.plot(self.dates, self.points, marker='o', color='lightblue', label='Points')  # Plot points

        # Plot linear regression line if model is provided
        if model:
            x_values = np.array([date.timestamp() for date in self.dates]).reshape(-1, 1)
            y_values = model.predict(x_values)
            ax.plot(self.dates, y_values, linestyle='-', color='orange', label='Prediction')

        # Format x-axis date labels
        date_fmt = mdates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(date_fmt)
        fig.autofmt_xdate(rotation=45)  # Rotate x-axis labels for better readability

        # Set labels for x-axis and y-axis
        ax.set_xlabel('Date', color='white')  # Set the color of the axis labels
        ax.set_ylabel('Points', color='white')  # Set the color of the axis labels
        ax.set_title(f'Points Over Time - {self.name}', color='white')  # Set the color of the title

        # Set y-axis ticks and labels
        ax.set_yticks(self.points)
        ax.set_yticklabels(formatted_points)

        # Set legend
        ax.legend()

        # Set the background color of the plot
        ax.set_facecolor(background_color)  # Use a dark background color
        fig.patch.set_facecolor(background_color)

        # Save the plot to an in-memory buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor=fig.get_facecolor())  # Explicitly set facecolor
        buf.seek(0)

        # Clear the plot to release memory
        plt.close(fig)

        return buf

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
