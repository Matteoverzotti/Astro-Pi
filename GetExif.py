import piexif

def extract_gps_data(image_path):
    # Load the image and extract the EXIF data
    exif_data = piexif.load(image_path)
    date_time = exif_data['0th'][306].decode()

    # Check if GPS data exists in the EXIF data
    if piexif.GPSIFD.GPSLatitude in exif_data['GPS'] and piexif.GPSIFD.GPSLongitude in exif_data['GPS']:
        latitude = exif_data['GPS'][piexif.GPSIFD.GPSLatitude]
        longitude = exif_data['GPS'][piexif.GPSIFD.GPSLongitude]
        altitude = exif_data['GPS'][piexif.GPSIFD.GPSAltitude]

        # Convert the latitude and longitude values to degrees
        latitude = _convert_to_degrees(latitude)
        longitude = _convert_to_degrees(longitude)
        altitude = altitude[0] / altitude[1]

        return date_time.split(' ')[1], latitude, longitude, altitude

    return None


def _convert_to_degrees(coordinate):
    degrees = coordinate[0][0] / coordinate[0][1]
    minutes = coordinate[1][0] / coordinate[1][1]
    seconds = coordinate[2][0] / coordinate[2][1]

    return (degrees, minutes, seconds)
