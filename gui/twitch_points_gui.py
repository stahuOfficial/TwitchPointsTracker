import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk

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


class TwitchPointsGUI:
    def __init__(self, twitch_points_list, models):
        self.window = tk.Tk()
        self.window.title("Twitch Points")
        self.window.iconbitmap("gui/twtracker.ico")
        self.window.geometry("1200x600")

        self.twitch_points_list = twitch_points_list
        self.twitch_points_models = models

        self.current_file = "twitch_points.csv"
        self.current_column = "percentage"

        # Dark theme
        self.window.configure(bg="#383838")
        style = ttk.Style()
        style.theme_use("default")
        style.configure(".", background="#383838", foreground="white", fieldbackground="#383838")
        style.map('.', background=[('selected', 'black')], foreground=[('selected', 'white')])
        style.map('Treeview', background=[('selected', '#4A6984')], foreground=[('selected', 'white')])

        top_streamer = None
        if len(self.twitch_points_list.streamers) > 0:
            top_streamer = self.twitch_points_list.streamers[0]
            for streamer in self.twitch_points_list.streamers:
                if streamer.points[-1] > top_streamer.points[-1]:
                    top_streamer = streamer

        self.plotted_streamer = top_streamer

        self.table = TwitchPointsTable(self.window, self.twitch_points_list)
        self.plot_img_tk = None
        if self.plotted_streamer:
            self.plot_frame, plot_img_tk = self.create_streamer_plot(self.plotted_streamer)
            self.plot_frame.grid(row=0, column=1, sticky="nsew")

        # Grid
        self.window.grid_columnconfigure(0, minsize=452)
        self.window.grid_columnconfigure(1, minsize=100)
        self.window.grid_rowconfigure(0, minsize=420)
        self.window.grid_rowconfigure(1, minsize=100)

        self.table.treeview.grid(row=0, column=0, columnspan=1)

        bottom_left_frame = tk.Frame(self.window, bg="#383838")
        bottom_left_frame.grid(row=1, column=0, sticky="nsew")

        self.name_entry = None
        self.points_entry = None
        self.target_entry = None
        self.create_control_buttons(bottom_left_frame)

        self.table.treeview.bind("<Button-1>", self.on_click)
        self.table.treeview.bind("<Double-1>", self.on_double_click)

        # Display the GUI
        self.window.lift()
        self.window.focus_force()
        self.window.mainloop()

    def run(self):
        self.window.mainloop()

    def on_click(self, event):
        region_clicked = self.table.treeview.identify("region", event.x, event.y)
        if region_clicked != "cell":
            return
        row_id = self.table.treeview.identify_row(event.y)
        row = self.table.treeview.item(row_id)["values"]
        streamer_name = str(row[1])
        self.plotted_streamer = self.twitch_points_list.get_entry(streamer_name)
        self.refresh_plot(self.plotted_streamer)

    def on_double_click(self, event):
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

        entry_widget.bind("<FocusOut>", lambda event: event.widget.destroy())
        entry_widget.bind("<Escape>", lambda event: event.widget.destroy())
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
            print("Adding streamer entry:")
            print(streamer.name, streamer.points[-1], streamer.target, str(streamer.dates[-1]))
        elif column_id == "#4":
            streamer.target = int(event.widget.get())
            streamer.est_date = self.twitch_points_models.when_target(streamer)
            self.twitch_points_list.save_to_file(self.current_file)
        self.table.refresh_df()
        self.table.refresh_table()
        self.refresh_plot(self.plotted_streamer)

        event.widget.destroy()

    def create_streamer_plot(self, streamer, height_px=420):
        # Create a frame for the plot
        plot_frame = tk.Frame(self.window, bg="#383838")
        model = self.twitch_points_models.models[streamer]

        # Create the Matplotlib plot
        plot_buffer = streamer.get_plot(model, height_px, background_color="#383838")  # Assuming get_plot() returns the image buffer
        plot_img = Image.open(plot_buffer)
        plot_img_tk = ImageTk.PhotoImage(plot_img)

        # Create a Canvas widget to display the plot
        canvas = tk.Canvas(plot_frame, bg="#ffffff", width=plot_img.width, height=plot_img.height, highlightthickness=0)
        canvas.pack(expand=True, fill="both")

        # Display the plot image on the canvas
        canvas.create_image(0, 0, anchor="nw", image=plot_img_tk)

        # Return the plot frame and plot image Tk object
        return plot_frame, plot_img_tk

    def create_control_buttons(self, frame):
        # Create the button frame within the bottom left frame
        button_frame = tk.Frame(frame, bg="#383838")
        button_frame.pack()

        # Create the add frame within the bottom left frame
        add_frame = tk.Frame(frame, bg="#383838")
        add_frame.pack()

        # Delete button
        delete_button = tk.Button(button_frame, text="Delete", command=self.delete_streamer, bg="#383838", fg="white")
        delete_button.pack()

        # Name label and entry
        name_label = tk.Label(add_frame, text="Name", bg="#383838", fg="white")
        name_label.pack()
        self.name_entry = tk.Entry(add_frame, bg="#383838", fg="white")
        self.name_entry.pack()

        # Points label and entry
        points_label = tk.Label(add_frame, text="Points", bg="#383838", fg="white")
        points_label.pack()
        self.points_entry = tk.Entry(add_frame, bg="#383838", fg="white")
        self.points_entry.pack()

        # Target label and entry
        target_label = tk.Label(add_frame, text="Target", bg="#383838", fg="white")
        target_label.pack()
        self.target_entry = tk.Entry(add_frame, bg="#383838", fg="white")
        self.target_entry.pack()

        # Add button
        add_button = tk.Button(add_frame, text="Add", command=self.add_streamer, bg="#383838", fg="white")
        add_button.pack()

    def add_streamer(self):
        streamer = Streamer(str(self.name_entry.get()),
                            int(self.points_entry.get()),
                            datetime.now(),
                            int(self.target_entry.get()))
        self.twitch_points_list.add_entry(streamer)

        self.twitch_points_models.construct_model(streamer)
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
            streamer_name = str(self.table.treeview.item(selected[0])["values"][1])
            streamer = self.twitch_points_list.get_entry(streamer_name)
            self.twitch_points_list.remove_entry(streamer)
            self.twitch_points_models.remove_model(streamer)

            self.table.refresh_df()
            self.table.refresh_table()
            self.twitch_points_models.save_models()
            self.twitch_points_list.save_to_file(self.current_file)

    def refresh_plot(self, streamer, height_px=420):
        # Create a new plot frame for the updated streamer
        new_plot_frame, new_plot_img_tk = self.create_streamer_plot(streamer, height_px)
        new_plot_frame.grid(row=0, column=1, sticky="nsew")

        if self.plot_frame:
            self.plot_frame.destroy()

        # Update the reference to the new plot frame and plot image Tk object
        self.plot_frame = new_plot_frame
        self.plot_img_tk = new_plot_img_tk
