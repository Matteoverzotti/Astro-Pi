# Declaring the libraries we need
import numpy as np
import matplotlib.pyplot as plt
import cv2
import csv
import os

import GetExif

# Our CONSTANTS
LAND_ALBEDO = 0.27
WATER_ALBEDO = 0.15
CLOUD_ALBEDO = 0.8
x = 7.654 * (10**(-3))
y = 5.476 * (10**(-3))
f = 6.8445 * (10**(-3))
sigma = 5.6703 * (10**(-8))
FLAT_SURFACE = 0.5063 * (10**(11))
K = 1360.772
DATA_FILE = "albedo_calculations.csv"

# Removes that useless band from the bottom-left corner
def removeBand(image):
    lower_code = np.array([0, 0, 90])
    upper_code = np.array([255, 255, 255])
    mask = cv2.inRange(image, lower_code, upper_code)
    h, w = mask.shape
    nr = 0
    plt.imshow(mask)
    for i in range(h):
        for j in range(w):
            if mask[i][j] == 0:
                nr += 1
    return nr


# Determine the number of blue/water pixels
def getWaterPixels(image): 
    lower_blue = np.array([90, 70, 50])
    upper_blue = np.array([130, 255, 255])
    mask = cv2.inRange(image, lower_blue, upper_blue)
    h, w = mask.shape
    nr = 0

    for i in range(h):
        for j in range(w):
            if mask[i][j] == 255:
                nr += 1

    return nr


# Determine the number of white/cloud pixels
def getCloudPixels(image):
    lower_white = np.array([0, 0, 180])
    upper_white = np.array([180, 30, 255])
    mask = cv2.inRange(image, lower_white, upper_white)
    h, w = mask.shape
    nr = 0

    for i in range(h):
      for j in range(w):
        if mask[i][j] == 255:
          nr += 1
    return nr


# Create csv file
def create_csv(data_file):
    with open(data_file, 'w') as f:
        writer = csv.writer(f)
        header = ("Time", "Image Name", "Latitude", "Longitude", "Altitude", "Albedo", "Temperature")
        writer.writerow(header)


# Adds data to the csv file
def add_csv_data(data_file, data):
    with open(data_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)
        f.flush()


# Load image
def load_image(image_path):
    print(image_path)
    image = cv2.imread(image_path) # Loading the image in BGR format
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) # Changing it to HSV

    return image


# Processes image
def process_image(image, elevation):
    height, width, useless = image.shape
    total = height * width - removeBand(image)

    waterPixels = getWaterPixels(image)
    cloudPixels = getCloudPixels(image)
    landPixels = total - waterPixels - cloudPixels

    totalAlbedo = ((waterPixels * WATER_ALBEDO) + (cloudPixels * CLOUD_ALBEDO) + (landPixels * LAND_ALBEDO)) / total

    # print(f"The total albedo is: {totalAlbedo}")
    surface = (elevation * elevation) * x * y / (f * f)
    temperature = ((((1 - totalAlbedo) * FLAT_SURFACE * K) / (sigma * surface)) ** (1 / 4))
    # print(f"The temperature is: {temperature} °K")

    return totalAlbedo, temperature



# Main function
def main():
    create_csv(DATA_FILE)
    files = os.listdir("selected_images")

    counter = 1
    for filename in files:
        print(counter)
        date, lat, long, alt = GetExif.extract_gps_data(f"selected_images/{filename}")

        image = load_image(f"selected_images/{filename}")
        albedo, temperature = process_image(image, alt)

        add_csv_data(DATA_FILE, (
                        date,
                        f"image_{counter}",
                        lat,
                        long,
                        alt,
                        albedo,
                        temperature
                     ))

        counter += 1
        print(date, lat, long, alt)


if __name__ == "__main__":
    main()