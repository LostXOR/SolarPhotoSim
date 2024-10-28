import time
import math
import numpy
from PIL import Image
import ephem
from sun_position_calculator import SunPositionCalculator

class Panel:
    def __init__(self, location, obstruction_map, tilt_azimuth, tilt_angle):
        """
        Instance of a solar panel.
        location: tuple of (latitude, longitude)
        obstruction_map: 2D numpy array of an equirectangular projection of the area, with north at x = 0. 0 represents non-obstructed and 1 represents obstructed
        tilt_azimuth: Azimuth the panel is tilted towards
        tilt_angle: Angle of the panel tilt (0 is horizontal)
        """
        self.location = location
        self.obstruction_map = obstruction_map
        self.az = tilt_azimuth
        self.alt = 90 - tilt_angle
        self.sun_calculator = SunPositionCalculator()

    def get_sun_position(self, unix_time):
        """Takes a unix timestamp, returns azimuth and altitude in radians"""
        pos = self.sun_calculator.pos(unix_time * 1000, *self.location)
        return pos.azimuth, pos.altitude

    def get_sun_obstruction(self, unix_time):
        """Get the amount of unobstructed Sun visible at a unix timestamp"""
        # Get position of Sun on map
        az, alt = self.get_sun_position(unix_time)
        x = round(obstruction_map.shape[1] * 0.5 * az / math.pi)
        y = round(obstruction_map.shape[0] * 0.5 - obstruction_map.shape[0] * alt / math.pi)
        r = obstruction_map.shape[1] // 1440 # Sun is 0.25 degrees in radius, map is 360 degrees
        # Get chunk of map with Sun
        sun = obstruction_map[y-r:y+r+1, y-r:y+r+1]

        # Mask out a circle and find the amount obstructed
        mask_x, mask_y = numpy.ogrid[:2*r+1, :2*r+1]
        mask = numpy.sqrt((mask_x - r) ** 2 + (mask_y - r) ** 2) < r + 0.5
        sun[~mask] = 0
        return numpy.sum(sun) / numpy.sum(mask)

    def get_sun_panel_angle(self, unix_time):
        """Get the angle between the Sun and the panel at a timestamp"""
        sun_az, sun_alt = self.get_sun_position(unix_time)
        sun_az, sun_alt = ephem.degrees(sun_az), ephem.degrees(sun_alt)
        panel_az, panel_alt = ephem.degrees(self.az * math.pi / 180), ephem.degrees(self.alt * math.pi / 180)
        return ephem.separation((panel_az, panel_alt), (sun_az, sun_alt))

    def get_panel_efficiency(self, unix_time):
        angle = self.get_sun_panel_angle(unix_time)
        obstruction = self.get_sun_obstruction(unix_time)
        if angle < math.pi / 2:
            return obstruction * math.cos(angle)
        else:
            return 0

location_lat = 46.7 # Minnesota
location_lon = 94.7
initial_timestamp = 1729950238
source_image_path = ""
obstruction_map_path = ""
heading = 100

# Get image data
img = Image.open(source_image_path) # Source image, with metadata
xmp_metadata = img.getxmp()["xmpmeta"]["RDF"]["Description"]
full_size = (int(xmp_metadata["FullPanoWidthPixels"]), int(xmp_metadata["FullPanoHeightPixels"]))
#heading = float(xmp_metadata["PoseHeadingDegrees"])

shift = heading / 360 * full_size[0] - full_size[0] // 2
offset = (int(xmp_metadata["CroppedAreaLeftPixels"]), int(xmp_metadata["CroppedAreaTopPixels"]))

img = Image.open(obstruction_map_path) # Obstruction map image, white = sky and black = obstruction


# Expand image to full size and align to north
img_expanded = img.crop((-offset[0], -offset[1], full_size[0] - offset[0], full_size[1] - offset[1]))
obstruction_map = numpy.roll(numpy.array(img_expanded), shift, axis = 1)[:,:,0]
obstruction_map[obstruction_map == 255] = 1

panel = Panel((location_lat, location_lon), obstruction_map, 180, 0)

average = 0
for timestamp in range(initial_timestamp, initial_timestamp + 86400 * 365, 600):
    average += panel.get_panel_efficiency(timestamp) / (86400 * 365 / 600)

print(average)
