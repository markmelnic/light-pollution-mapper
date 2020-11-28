import googlemaps
from math import sqrt
from scipy.spatial import distance

from lpm.settings import COLORS


class LPM:
    def __init__(self, kmz_obj, api_key: str) -> None:
        self.kmz_obj = kmz_obj
        self.gmaps = googlemaps.Client(key=api_key)

    def get_pollution(self, location: str) -> list:
        user_coords = self._user_location(location)
        item = self.kmz_obj._find_coords_item(user_coords)
        image = self.kmz_obj._load_images(item[1], single=True)
        closest_unique_spots = self._find_pollution_coords(user_coords, item, image)
        return closest_unique_spots

    def _user_location(self, location: str) -> tuple:
        geocoded_location = self.gmaps.geocode(location)
        lat = geocoded_location[0]["geometry"]["location"]["lat"]
        lng = geocoded_location[0]["geometry"]["location"]["lng"]
        return (lat, lng)

    def _find_pollution_coords(self, user_coords: list, item: list, image: bytes) -> list:
        def _matrix_geo_coords(matrix_coords: list) -> tuple:
            lat = item[3] - ((item[3] - item[4]) / width * matrix_coords[1])
            lng = item[6] + ((item[5] - item[6]) / height * matrix_coords[0])
            return (lat, lng)

        def _closest_color(rgb: list) -> tuple:
            r, g, b = rgb
            color_diffs = []
            for color in COLORS:
                cr, cg, cb = color
                color_diff = sqrt(abs(r - cr) ** 2 + abs(g - cg) ** 2 + abs(b - cb) ** 2)
                color_diffs.append((color_diff, color))
            return min(color_diffs)[1]

        def _closest(node: tuple, nodes: list) -> tuple:
            closest_px = distance.cdist([node], nodes).argmin()
            return nodes[closest_px]

        width, height = image.size
        wpx = int(height * (user_coords[1] - item[6]) / (item[5] - item[6]))
        hpx = width - int(width * (user_coords[0] - item[4]) / (item[3] - item[4]))
        pixelmap = image.load()
        data = {}
        for c in COLORS:
            data[COLORS.index(c)] = []
        for i in range(int(width / 2)):
            for j in range(int(height / 2)):
                color = _closest_color(pixelmap[i * 2, j * 2])
                for c in COLORS:
                    if color == c:
                        data[COLORS.index(c)].append([i * 2, j * 2])

        closest_unique_spots = [
            _matrix_geo_coords(_closest((wpx, hpx), data[COLORS.index(c)])) for c in COLORS
        ]
        return closest_unique_spots
