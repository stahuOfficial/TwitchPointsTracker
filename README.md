# TwitchPointsTracker
A Python program with a Tkinter GUI that helps you track your Twitch points and estimates reaching targets with linear regression.

## Features

- **Streamers Table:** You can add streamers to the table, which displays their names and the points you've accumulated on their channels.

- **Manual Points Entry:** You can manually enter the points you have on each streamer's channel. This allows you to keep track of your progress accurately.

- **Points Over Time Plot:** The program generates a plot showing your points over time. It also predicts when you will achieve your points target based on your current rate of accumulation.

## Prerequisites

- Python 3.x
- Tkinter library (usually comes pre-installed with Python)
- Matplotlib library (`pip install matplotlib`)

## How to Use

### Method 1: Batch File

1. Clone this repository to your local machine.
2. Create a `.bat` file in your desired location.
3. Edit the file and paste these lines, make sure to replace `<FileLocation>` and `<DriveName>` with the correct information.
    ```batch
    @echo off
    <DriveName>:
    cd <FileLocation>\TwitchPointsTracker
    python <FileLocation>\TwitchPointsTracker\main.py
    ```
4. Double-click the bat file.
5. The program window will open. You can now interact with the GUI to add streamers, enter points manually, and view your points over time plot.

### Method 2: Manual Execution

1. Clone this repository to your local machine.
2. Navigate to the directory containing the `main.py` file.
3. Run the program by executing the following command: `python main.py`
4. The program window will open. You can now interact with the GUI to add streamers, enter points manually, and view your points over time plot.

#### Note: 
- Make sure Python is added to your system PATH for the batch file to work properly.
- You may need to modify the batch file (`TwitchPointsTracker.bat`) to reflect the correct paths according to your system configuration.

## Usage Tips

- **Adding Streamers:** Below the table, fill in the fields and click the "Add" button.
- **Entering Points:** Double-click on a streamer's points to enter your points manually.
- **Viewing Plot:** Just click on the streamer whose plot you want to view.

## Contributing

Contributions are welcome! If you have any suggestions, improvements, or bug fixes, feel free to open an issue or create a pull request.
