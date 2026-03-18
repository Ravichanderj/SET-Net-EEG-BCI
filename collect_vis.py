import serial
import csv
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# === Configuration ===
COM_PORT = 'COM3'        # Change as needed
BAUD_RATE = 115200       # Match with Arduino code
DURATION = 300           # Total duration to collect data (seconds)
MAX_POINTS = 500         # Number of points to show in the live plot

# === Setup Serial Port ===
ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Give some time to establish the connection

# === Create CSV File ===
csv_file = open('eeg_signal.csv', 'a', newline='')
csv_writer = csv.writer(csv_file)

# === Data Storage for Plot ===
timestamps = deque(maxlen=MAX_POINTS)
eeg_values = deque(maxlen=MAX_POINTS)

# === Plot Setup ===
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.set_title("Live EEG Signal from Arduino")
ax.set_xlabel("Time (s)")
ax.set_ylabel("EEG Value")
ax.grid(True)

start_time = time.time()

def update_plot(frame):
    global start_time
    if time.time() - start_time > DURATION:
        print("Data collection complete.")
        plt.close()
        return

    try:
        data = ser.readline().decode("latin-1").strip()
        values = data.split(',')

        if len(values) > 0 and values[0].isdigit():
            eeg_value = int(values[0])
            elapsed_time = round(time.time() - start_time, 2)
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

            timestamps.append(elapsed_time)
            eeg_values.append(eeg_value)

            csv_writer.writerow([timestamp, eeg_value])

            # Update plot data
            line.set_data(timestamps, eeg_values)
            ax.relim()
            ax.autoscale_view()

    except Exception as e:
        print("Error:", e)

    return line,

# === Start Live Plot Animation ===
ani = animation.FuncAnimation(fig, update_plot, blit=False, interval=50)
plt.tight_layout()
plt.show()

# === Cleanup ===
ser.close()
csv_file.close()
