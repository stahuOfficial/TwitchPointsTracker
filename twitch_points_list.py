import csv
import io

import numpy as np
import pandas as pd
from datetime import datetime

from matplotlib import pyplot as plt
from matplotlib import dates as mdates


def evenly_spaced_list(a, b, num_elements):
    step = (b - a) / (num_elements - 1) if num_elements > 1 else 0
    return [a + i * step for i in range(num_elements)]


def concatenate_dates(dates):
    """
    Concatenate dates that are on the same day.
    :param dates: list of dates
    :return: list of dates with the same date concatenated
    """
    unique_dates = []
    reversed_dates = dates[::-1]
    for date in reversed_dates:
        if date.date() not in [unique_date.date() for unique_date in unique_dates]:
            unique_dates.append(date)
    return unique_dates[::-1]


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
                writer.writerow([streamer.name, streamer.points[0], streamer.dates[0], streamer.target])
                for i in range(1, len(streamer.points)):
                    writer.writerow([streamer.name, streamer.points[i], streamer.dates[i]])

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
                [streamer, streamer.name, streamer.points[-1], streamer.target, percentage, streamer.est_date])

        columns = ["streamer_object", "name", "points", "target", "percentage", "est_date"]
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

    def get_plot(self, model=None, height_px=450, background_color='#2b2b2b'):
        # Calculate the width based on the desired height and the aspect ratio (16:9)
        width_px = int(height_px * (16 / 9))

        # Convert width and height from pixels to inches
        width_in = width_px / 100
        height_in = height_px / 100

        plt.style.use('dark_background')

        # Plotting
        fig, ax = plt.subplots(figsize=(width_in, height_in))
        ax.plot(self.dates, self.points,
                marker='o',
                color='lightblue',
                label='Points',
                markerfacecolor=background_color,
                markeredgewidth=1.3)  # Plot points

        filled_points = [True if date in concatenate_dates(self.dates) else False for date in self.dates]
        for i in range(len(self.dates)):
            if filled_points[i]:
                ax.plot(self.dates[i], self.points[i],
                        marker='o',
                        color='lightblue')

        if model and model.coef_ != 0:
            x_values = np.array([date.timestamp() for date in self.dates]).reshape(-1, 1)
            y_values = model.predict(x_values)
            ax.plot(self.dates, y_values, linestyle='-', color='orange', label='Prediction')

        # Format x-axis date labels
        date_fmt = mdates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(date_fmt)

        ax.set_xlabel('Date', color='white')
        ax.set_ylabel('Points', color='white')
        ax.set_title(f'Points Over Time - {self.name}', color='white')

        num_ticks = 5
        tick_positions = np.linspace(min(self.points), max(self.points), num_ticks)
        ax.set_yticks(tick_positions)
        ytick_labels = evenly_spaced_list(min(self.points), max(self.points), num_ticks)
        ax.set_yticklabels([format(int(label), ",").replace(",", " ") for label in ytick_labels])

        ax.legend()

        # Add text annotation for target
        formatted_date = self.est_date.strftime(
            '%d-%m-%Y') if self.est_date and self.est_date != datetime.max else 'N/A'
        ax.text(0, 1.047, f'Target: {format(self.target, ",").replace(",", " ")}\n'
                          f'Est. date: {formatted_date}',
                horizontalalignment='left',
                verticalalignment='center',
                transform=ax.transAxes,
                fontsize=8,
                color='lightgray')

        # Set the background color of the plot
        ax.set_facecolor(background_color)  # Use a dark background color
        fig.patch.set_facecolor(background_color)

        # Save the plot to an in-memory buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
        buf.seek(0)

        # Clear the plot to release memory
        plt.close(fig)

        return buf

    def __str__(self):
        return str(self.name) + " " + str(self.points) + " " + str([str(date) for date in self.dates]) \
               + " " + str(self.target)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
