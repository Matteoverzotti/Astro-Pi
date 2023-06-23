import os
import piexif
from fractions import Fraction

def to_deg(value, loc):
    """convert decimal coordinates into degrees, munutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60, 5)
    return (deg, min, sec, loc_value)

def change_to_rational(number):
    """convert a number to rantional
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return (f.numerator, f.denominator)


def set_gps_location(file_name, lat, lng, altitude):
    """Adds GPS position as EXIF metadata
    Keyword arguments:
    file_name -- image file
    lat -- latitude (as float)
    lng -- longitude (as float)
    altitude -- altitude (as float)
    """
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])

    exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
    exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
        piexif.GPSIFD.GPSAltitudeRef: 1,
        piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude)),
        piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
        piexif.GPSIFD.GPSLatitude: exiv_lat,
        piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
        piexif.GPSIFD.GPSLongitude: exiv_lng
    }

    gps_exif = {"GPS": gps_ifd}

    # get original exif data first!
    exif_data = piexif.load(file_name)

    # update original exif data to include GPS tag
    exif_data.update(gps_exif)
    exif_bytes = piexif.dump(exif_data)

    piexif.insert(exif_bytes, file_name)


with open('total_interval_sec.csv', 'r') as f:
    contents = f.read().split('\n')
    for i in range(1, len(contents)):
        line = contents[i].split(',')

        date = line[0]

        latitude = float(line[7])
        longitude = float(line[8])
        altitude = float(line[9]);

        hour = date[:2]
        min = date[3:5]
        sec = date[6:8]

        files = os.listdir("selected_images")

        stringname = f"{hour}-{min}-{sec}.jpg"

        if stringname not in files:
            continue

        set_gps_location(f"Images_EXIF/{stringname}", latitude, longitude, altitude)