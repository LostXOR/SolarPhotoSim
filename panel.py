import math
import numpy
import ephem
from sun_position_calculator import SunPositionCalculator

sun_calculator = SunPositionCalculator()

class Panel:
    def __init__(self, lat, lon, obstruction_map, tilt_azimuth, tilt_angle):
        """
        Instance of a solar panel.
        lat, lon: Latitude and longitude of panel
        obstruction_map: 2D numpy array of an equirectangular projection of the area, with north at x = 0
            0 = obstructed, 1 = non-obstructed, 2 = undefined
        tilt_azimuth: Azimuth of the panel
        tilt_angle: Angle the panel is tilted (0 is horizontal)
        """
        self.location = (lat, lon)
        self.obstruction_map = obstruction_map
        self.facing = (tilt_azimuth, 90 - tilt_angle) # We want the direction it's facing

    def get_sun_position(self, unix_time):
        """Takes a unix timestamp, returns azimuth and altitude in radians"""
        pos = sun_calculator.pos(unix_time * 1000, *self.location)
        return pos.azimuth, pos.altitude

    def get_sun_obstruction(self, unix_time):
        """Get the amount of unobstructed Sun visible at a unix timestamp"""
        # Get position of Sun on map
        az, alt = self.get_sun_position(unix_time)
        x = round(self.obstruction_map.shape[1] * 0.5 * az / math.pi)
        y = round(self.obstruction_map.shape[0] * 0.5 - self.obstruction_map.shape[0] * alt / math.pi)

        # Get chunk of map with Sun
        r = self.obstruction_map.shape[1] // 1440 # Sun is 0.25 degrees in radius, map is 360 degrees
        sun = self.obstruction_map[y-r:y+r+1, y-r:y+r+1]

        # Mask out a circle and find the amount obstructed
        mask_x, mask_y = numpy.ogrid[:2*r+1, :2*r+1]
        mask = numpy.sqrt((mask_x - r) ** 2 + (mask_y - r) ** 2) < r + 0.5
        sun[~mask] = 0
        mask[sun == 2] = 0

        # Results are not valid if no valid pixels in area
        if numpy.sum(mask == 1) == 0:
            return None
        return numpy.sum(sun == 1) / numpy.sum(mask == 1)

    def get_sun_panel_angle(self, unix_time):
        """Get the angle between the Sun and the panel at a timestamp"""
        sun_az, sun_alt = self.get_sun_position(unix_time)
        sun_az, sun_alt = ephem.degrees(sun_az), ephem.degrees(sun_alt)
        panel_az, panel_alt = ephem.degrees(self.facing[0] * math.pi / 180), ephem.degrees(self.facing[1] * math.pi / 180)
        return ephem.separation((panel_az, panel_alt), (sun_az, sun_alt))

    def get_panel_efficiency(self, unix_time):
        angle = self.get_sun_panel_angle(unix_time)
        obstruction = self.get_sun_obstruction(unix_time)
        if obstruction is None:
            return None
        # If angle is > 90 deg, the panel is facing away from the Sun
        if angle < math.pi / 2:
            return obstruction * math.cos(angle)
        else:
            return 0
