import tkinter as tk
from tkinter import ttk

from twitch_points_list import TwitchPointsList

colors = ["orange red",
          "tomato",
          "orange",
          "gold",
          "yellow",
          "light yellow",
          "green yellow",
          "pale green",
          "light green",
          "green2",
          "cyan2"]


def get_column_index(column_name):
    """
    Get the index of a column name.

    Args:
    - column_name (str): The name of the column.

    Returns:
    - int: The index of the column.
    """
    if column_name == "name":
        return 1
    elif column_name == "points":
        return 2
    elif column_name == "target":
        return 3
    elif column_name == "percentage":
        return 4
    elif column_name == "est_date":
        return 5


def sort_table(lst, column, reverse=False):
    """
    Sort a list of lists based on a specific column index.

    Args:
    - lst (list): The list of lists to be sorted.
    - column_index (int): The index of the column to sort by.
    - reverse (bool): Whether to sort in descending order. Default is False.

    Returns:
    - list: The sorted list of lists.
    """
    column_index = get_column_index(column)
    return sorted(lst, key=lambda x: x[column_index], reverse=reverse)


class TwitchPointsTable:
    def __init__(self, parent, twitch: TwitchPointsList):
        self.twitch = twitch
        self.df = twitch.to_df()
        self.window = parent

        self.up_triangle = tk.PhotoImage(file="gui/up_triangle.png")
        self.down_triangle = tk.PhotoImage(file="gui/down_triangle.png")

        self.current_sort_column = "percentage"

        # Streamers table
        self.treeview = ttk.Treeview(self.window, columns=("#", "name", "points", "target", "percentage", "est_date"),
                                     show="headings", height=20)
        self.column_names = {"#": "#",
                             "name": " Streamer",
                             "points": " Points",
                             "target": " Target",
                             "percentage": " %",
                             "est_date": " Est. Date"}

        self.treeview.column("#", width=20, anchor="center")
        self.treeview.heading("#", text="#", anchor="center")

        self.treeview.column("name", width=100, anchor=tk.W)
        self.treeview.heading("name", text=self.column_names["name"], anchor=tk.W,
                              command=lambda: self.sort_column("name"))

        self.treeview.column("points", width=80, anchor=tk.E)
        self.treeview.heading("points", text=self.column_names["points"], anchor=tk.W,
                              command=lambda: self.sort_column("points"))

        self.treeview.column("target", width=80, anchor=tk.E)
        self.treeview.heading("target", text=self.column_names["target"], anchor=tk.W,
                              command=lambda: self.sort_column("target"))

        self.treeview.column("percentage", width=60, anchor=tk.E)
        self.treeview.heading("percentage", text=self.column_names["percentage"], anchor=tk.W,
                              command=lambda: self.sort_column("percentage"))

        self.treeview.column("est_date", width=112, anchor=tk.W)
        self.treeview.heading("est_date", text=self.column_names["est_date"], anchor=tk.W,
                              command=lambda: self.sort_column("est_date"))

        self.sort_order = {"#": True, "name": True, "points": True, "target": True, "percentage": False,
                           "est_date": True}

        self.treeview.focus_set()

        self.refresh_table()

    def refresh_table(self):
        self.treeview.delete(*self.treeview.get_children())
        self.df = self.df.sort_values(by=self.current_sort_column, ascending=self.sort_order[self.current_sort_column])
        for i, entry in enumerate(self.df.itertuples(), start=1):
            user = entry.name
            points = entry.points
            target = entry.target
            percentage = entry.percentage
            est_date = entry.est_date
            # Determine the background color based on the percentage
            color = colors[min(int(percentage / 10), len(colors) - 1)]
            # Insert the row with the specified background color
            self.treeview.insert("", "end", values=(i,
                                                    user,
                                                    format(points, ',').replace(',', ' '),
                                                    format(target, ',').replace(',', ' '),
                                                    format(percentage, '.2f') + "%", est_date),
                                 tags=(color,))
        # Configure the tags to set the background color
        for color in colors:
            self.treeview.tag_configure(color, background=color)

    def refresh_df(self):
        self.df = self.twitch.to_df()

    def sort_column(self, column):
        self.df = self.df.sort_values(by=column, ascending=self.sort_order[column])
        self.current_sort_column = column
        self.sort_order[column] = not self.sort_order[column]

        # Update the table widget with the sorted data
        self.refresh_table()

        # Update the column headings with sort arrows
        for col in self.treeview["columns"]:
            if col == column:
                if self.sort_order[column]:
                    self.treeview.heading(col, image=self.up_triangle, text=self.column_names[col])
                else:
                    self.treeview.heading(col, image=self.down_triangle, text=self.column_names[col])
            else:
                self.treeview.heading(col, image='', text=self.column_names[col])
