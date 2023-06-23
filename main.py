"""
**** NARWHALS TEAM ****
OBJECTIVE:
The objective of the experiment is to collect all necessary data, measured and calculated.

By analyzing the collected data we want to study:
    - The albedo of the scanned areas;
    - The medium Earth Temperature, based of those areas;

CODE:
A. Configuration
    Defining and creating the necessary subprograms for:
    - ISS location (it is important to use the latest TLE data and to have
    the Ed's clock set as Greenwich Mean Time, GMT, the clock used for ISS tracking);
    - Files management;
B. Initialization of the working variables and creating the data files
C. Main program
    - Measurements, storage and display -> 175 minutes;
We will store data for the whole experiment, at 10 seconds interval.
We also take pictures, at 15 seconds interval,
Also we will capture a 5 second video at 10 minutes interval. We didn't import 
threading, so while the program is capturing the video everything else stops.
"""

from sense_hat import SenseHat
from time import sleep
from orbit import ISS
from datetime import datetime, timedelta
from logzero import logger, logfile
from picamera import PiCamera
from pathlib import Path
import csv
import numpy as np

# I. FILES MANAGEMENT

# Set up Sense Hat and initialization
sense = SenseHat()
sense.set_imu_config(True, True, True)

# Set a logfile name
dir_path = Path(__file__).parent.resolve()
logfile(dir_path/"Narwhals.log")

# Create a new CSV data_file and add the header row
def create_csv_file(data_file):
    with open(data_file, 'w') as f:
        writer = csv.writer(f)
        header = ("Date/Time",
                "a_x", "a_y", "a_z",
                "w_x", "w_y", "w_z",
                "Latitude", "Longitude", "Elevation",
                "Pitch", "Roll", "Yaw",
                "Pitch_accel_only", "Roll_accel_only", "Yaw_accel_only", 
                "Pitch_gyro_only", "Roll_gyro_only", "Yaw_gyro_only")
        writer.writerow(header)

# Add a new data row at an existing CSV data_file
def add_csv_data(data_file, data):
    with open(data_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)
        f.flush()

# Function that captures a photo
camera = PiCamera()
camera.resolution = (1920, 1080)
def capture_photo(filename):
    img_path = '{dir_path}/{date}.jpg'.format(dir_path=dir_path, date=filename)
    # Capture the image
    camera.capture(img_path)

# Function that captures a video
# While the video is being captured, the rest of the program halts
def capture_video(filename):
    video_path = '{dir_path}/{date}.h264'.format(dir_path=dir_path, date=filename)
    camera.start_recording(video_path)
    sleep(5)
    camera.stop_recording()

# II. INITIALIZATION OF THE VARIABLES

# Variables for storing intervals
interval_sec_data = 10
interval_sec_photo = 15
interval_mnt = 10
contor_sec_data = 0
contor_sec_photo = 0
contor_mnt = 0

# Create data storage file
total_interval_sec = dir_path/"total_interval_sec.csv"
create_csv_file(total_interval_sec)

# Current date/time
now_time = datetime.now()
sec_old = now_time.second
mnt_old = now_time.minute
start_time = datetime.now()


# III. MAIN PROGRAM

# The main program will run for 175 minutes
while (now_time < start_time + timedelta(minutes = 175)):
    try:
        # IMU sensor: acceleration and angular velocity
        # on x , y , z axis

        acceleration = sense.get_accelerometer_raw()
        a_x = acceleration["x"]
        a_y = acceleration["y"]
        a_z = acceleration ["z"]

        angular_velocity = sense.get_gyroscope_raw()
        w_x = angular_velocity["x"]
        w_y = angular_velocity["y"]
        w_z = angular_velocity["z"]

        # Contribution of individual sensor to the orientation of the Sense Hat
        sense.set_imu_config(True, False, False)
        accel_only = sense.get_accelerometer()
        pitch_accel_only = accel_only["pitch"]
        roll_accel_only = accel_only["roll"]
        yaw_accel_only = accel_only["yaw"]

        sense.set_imu_config(False, True, False)
        gyro_only = sense.get_gyroscope()
        pitch_gyro_only = gyro_only["pitch"]
        roll_gyro_only = gyro_only["roll"]
        yaw_gyro_only = gyro_only["yaw"]

        # Orientation of the Sense Hat with all the sensors enabled
        sense.set_imu_config(True, True, True)
        orientation = sense.get_orientation_degrees()
        pitch = orientation["pitch"]
        roll = orientation["roll"]
        yaw = orientation["yaw"]

        # ISS current position
        location = ISS.coordinates()
        # print(location)
        # print("Latitude: {latitudine}".format(latitudine = location.latitude.degrees))
        # print("Longitude: {longitudine}".format(longitudine = location.longitude.degrees))
        # print("Altitude: {altitudine}".format(altitudine = location.elevation.m))

        lat = location.latitude.degrees
        long = location.longitude.degrees
        elev = location.elevation.m

        # Current time
        now_time = datetime.now()
        yr = now_time.year
        mnh = now_time.month
        dy = now_time.day
        hr = now_time.hour
        mnt = now_time.minute
        sec = now_time.second

        # Complex data for storage
        data = (
            now_time,
            a_x, a_y, a_z,
            w_x, w_y, w_z,
            lat, long, elev,
            pitch, roll, yaw,
            pitch_accel_only, roll_accel_only, yaw_accel_only,
            pitch_gyro_only, roll_gyro_only, yaw_gyro_only
        )
        
        # Counter for storage
        if sec != sec_old:
            contor_sec_data = contor_sec_data + 1
            contor_sec_photo = contor_sec_photo + 1
            sec_old = sec
        if mnt != mnt_old:
            contor_mnt = contor_mnt + 1
            mnt_old = mnt

        if contor_sec_data >= interval_sec_data:
            contor_sec_data = 0
            add_csv_data(total_interval_sec, data)
        if contor_sec_photo >= interval_sec_photo:
            contor_sec_photo = 0
            capture_photo(now_time.strftime('%y.%m.%d_%H-%M-%S'))
        if contor_mnt >= interval_mnt:
            contor_mnt = 0
            capture_video(now_time.strftime('%y.%m.%d_%H-%M-%S'))

        
    except Exception as e:
        logger.error('{}: {}'.format(e.__class__.__name__,e))


# Fin.

