import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from tkinter import ttk

from gui.twitch_points_table import TwitchPointsTable
from twitch_points_list import Streamer
from twitch_points_models import TwitchPointsModels


def format_number(num, precision=2):
    """
    Format a number to a string with a given precision
    :param num: number to be formatted
    :param precision: number of decimal places
    """
    if abs(num) >= 1e6 or abs(num) < 1e-2:
        return format(num, f".{precision}e")
    else:
        return format(num, f".{precision}f").rstrip('0').rstrip('.')


def on_focus_out(event):
    event.widget.destroy()


class TwitchPointsGUI:
    def __init__(self, twitch_points_list, models: TwitchPointsModels):
        self.open_file = None
        self.window = tk.Tk()
        self.window.title("Twitch Points")
        self.window.geometry("500x600")

        self.current_file = "twitch_points.csv"

        self.twitch_points_list = twitch_points_list
        self.twitch_points_models = models

        self.current_column = "percentage"
        # self.twitch_points_list.sort(self.current_column, True)

        # Set dark theme
        self.window.configure(bg="#383838")
        style = ttk.Style()
        style.theme_use("default")
        style.configure(".", background="#383838", foreground="white", fieldbackground="#383838")
        style.map('.', background=[('selected', 'black')], foreground=[('selected', 'white')])
        style.map('Treeview', background=[('selected', '#4A6984')], foreground=[('selected', 'white')])

        self.table = TwitchPointsTable(self.window, self.twitch_points_list)
        self.table.refresh_table()
        self.table.treeview.pack()

        # Buttons
        button_frame = tk.Frame(self.window, bg="#383838")
        button_frame.pack()

        add_frame = tk.Frame(self.window, bg="#383838")
        add_frame.pack()

        # Delete button
        delete_button = tk.Button(button_frame, text="Delete", command=self.delete_streamer, bg="#383838", fg="white")
        delete_button.pack()

        name_label = tk.Label(add_frame, text="Name", bg="#383838", fg="white")
        name_label.pack()
        self.name_entry = tk.Entry(add_frame, bg="#383838", fg="white")
        self.name_entry.pack()

        points_label = tk.Label(add_frame, text="Points", bg="#383838", fg="white")
        points_label.pack()
        self.points_entry = tk.Entry(add_frame, bg="#383838", fg="white")
        self.points_entry.pack()

        target_label = tk.Label(add_frame, text="Target", bg="#383838", fg="white")
        target_label.pack()
        self.target_entry = tk.Entry(add_frame, bg="#383838", fg="white")
        self.target_entry.pack()

        # create add button
        add_button = tk.Button(add_frame, text="Add", command=self.add_streamer, bg="#383838", fg="white")
        add_button.pack()

        self.table.treeview.bind("<Double-1>", self.on_click)

        self.window.mainloop()

    def run(self):
        self.window.mainloop()

    def add_streamer(self):
        streamer = Streamer(self.name_entry.get(), int(self.points_entry.get()), datetime.now(),
                            int(self.target_entry.get()))
        self.twitch_points_list.add_entry(streamer)
        self.twitch_points_models.models[streamer] = self.twitch_points_models.construct_model(streamer)
        streamer.est_date = self.twitch_points_models.when_target(streamer)
        self.table.refresh_df()
        self.table.refresh_table()
        self.twitch_points_models.save_models()
        self.twitch_points_list.save_to_file(self.current_file)

        self.name_entry.delete(0, 'end')
        self.points_entry.delete(0, 'end')
        self.target_entry.delete(0, 'end')

    def delete_streamer(self):
        selected = self.table.treeview.selection()

        if selected:
            # open pop up box to verify deletion
            if not messagebox.askokcancel("Delete Streamer", "Are you sure you want to delete this streamer?"):
                return
            streamer = self.twitch_points_list.get_entry(self.table.treeview.item(selected[0])["values"][1])
            self.twitch_points_list.remove_entry(streamer)
            self.twitch_points_models.remove_model(streamer)
            self.table.refresh_df()
            self.table.refresh_table()
            self.twitch_points_models.save_models()
            self.twitch_points_list.save_to_file(self.current_file)

    def on_click(self, event):
        region_clicked = self.table.treeview.identify("region", event.x, event.y)
        if region_clicked != "cell":
            return
        column_id = self.table.treeview.identify_column(event.x)
        row_id = self.table.treeview.identify_row(event.y)
        row = self.table.treeview.item(row_id)["values"]
        streamer = self.twitch_points_list.get_entry(row[1])

        if column_id in ["#2", "#3", "#4"]:  # Streamer name
            selected_text = self.table.treeview.item(row_id)["values"][int(column_id[1]) - 1]
            x, y, w, h = self.table.treeview.bbox(row_id, column_id)
            self.entry_widget(self.table.treeview, streamer, column_id, selected_text, x, y, w, h)

    def entry_widget(self, tree, streamer, column_id, selected_text, x, y, w, h):
        entry_widget = tk.Entry(tree, borderwidth=0, width=10)
        entry_widget.place(x=x, y=y, width=w, height=h)

        entry_widget.insert(0, selected_text)
        entry_widget.select_range(0, 'end')

        entry_widget.focus()

        entry_widget.bind("<FocusOut>", lambda event: on_focus_out(event))
        entry_widget.bind("<Escape>", lambda event: on_focus_out(event))
        entry_widget.bind("<Return>", lambda event: self.on_return(event, streamer, column_id))

    def on_return(self, event, streamer, column_id):
        if column_id == "#2":
            old_name = streamer.name
            streamer.name = event.widget.get()
            self.twitch_points_models.models[streamer] = self.twitch_points_models.models.pop(old_name)
        elif column_id == "#3":
            streamer.add_entry(int(event.widget.get()), datetime.now())
            self.twitch_points_models.construct_model(streamer)
            self.twitch_points_models.save_models()
            self.twitch_points_list.save_to_file(self.current_file)
            streamer.est_date = self.twitch_points_models.when_target(streamer)
        elif column_id == "#4":
            streamer.target = int(event.widget.get())
            streamer.est_date = self.twitch_points_models.when_target(streamer)
            self.twitch_points_list.save_to_file(self.current_file)
        self.table.refresh_df()
        self.table.refresh_table()

        event.widget.destroy()
