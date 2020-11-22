import glob, csv, os
import pandas as pd
from math import sqrt
from lxml import html
from zipfile import ZipFile
from PIL import Image

pd.options.mode.chained_assignment = None

COLORS = [
    (255, 255, 255), # white
    (220, 190, 250), # light purple
    (240, 110, 250), # purple
    (230, 0, 0),     # red
    (255, 85, 10),   # orange
    (255, 255, 0),   # yellow
    (50, 140, 0),    # green
    (0, 150, 210),   # light blue
    (10, 75, 180),   # blue
    (0, 35, 115),    # dark blue
    (128, 128, 128), # light grey
    (77, 77, 77),    # dark grey
    (0, 0, 0),       # black
]

ZIP_KML_DOC = "doc.kml"
CSV_KML_DOC = "kml_index.csv"
ZIP_KMZ_IMG_FOLDER = "files"
KMZ_GLOBAL_IMAGE = "map.jpg"

class KMZ:
    def __init__(self) -> None:
        self.kmz_zip = ZipFile(glob.glob("*.kmz")[0], "r")
        if not os.path.isfile(CSV_KML_DOC):
            self.kml_file = self.kmz_zip.open(ZIP_KML_DOC, "r").read()
            self._generate_csv()
        self._load_df()
        self._arrange_df()

    def _generate_csv(self,) -> None:
        kml_content = html.fromstring(self.kml_file)
        with open(CSV_KML_DOC, "w", newline="") as kml_csv:
            kml_csv_writer = csv.writer(kml_csv)
            kml_csv_writer.writerow(
                ["index", "image", "draw_order", "north", "south", "east", "west", "rotation"]
            )
            for item in kml_content.cssselect("Document GroundOverlay"):
                image = item.cssselect("name")[0].text_content()
                index = image[23:-4]
                draw_order = item.cssselect("drawOrder")[0].text_content()
                coords = item.cssselect("LatLonBox")[0]
                north = coords.cssselect("north")[0].text_content()
                south = coords.cssselect("south")[0].text_content()
                east = coords.cssselect("east")[0].text_content()
                west = coords.cssselect("west")[0].text_content()
                rotation = coords.cssselect("rotation")[0].text_content()
                kml_csv_writer.writerow(
                    [index, image, draw_order, north, south, east, west, rotation]
                )

    def _load_df(self, ) -> None:
        self.df = pd.read_csv(CSV_KML_DOC)
        self.df.sort_values(by='north', ascending=False, inplace = True)

    def _arrange_df(self, ) -> None:
        self.globe_matrix = []
        for i, row in self.df.iterrows():
            sub_df = self.df.loc[(self.df['north'] == row['north']) & (self.df['south'] == row['south'])]
            if sub_df.empty:
                continue
            else:
                sub_df.sort_values(by='west', inplace = True)
                self.globe_matrix.append(sub_df)
                self.df.drop(sub_df.index, inplace = True)

    def _find_coords_item(self, coords: list) -> list:
        if myloc[0] > 0: # first 10
            gset = [None, -7]
            if myloc[1] > 0: # last 21
                sset = [22, None]
            else:
                sset = [None, -21]
        else: # last 7
            gset = [10, None]
            if myloc[1] > 0: # last 21
                sset = [22, None]
            else:
                sset = [None, -21]

        for item in self.globe_matrix[gset[0]:gset[1]]:
            for i, row in item.iloc[sset[0]:sset[1]].iterrows():
                if (row['north'] >= myloc[0] >= row['south']) and (row['west'] <= myloc[1] <= row['east']):
                    return row.tolist()

    def _find_coords_image(self, user_coords, item, image):
        width, height = image.size
        print(width, height)
        wpx = int(height*(user_coords[1]-item[6])/(item[5]-item[6]))
        hpx = width - int(width*(user_coords[0]-item[4])/(item[3]-item[4]))
        print(wpx, hpx)
        pixelmap = image.load()
        for i in range(width/2):
            for j in range(height/2):
                color = self._closest_color(pixelmap[i*2, j*2])

    def _closest_color(self, rgb):
        r, g, b = rgb
        color_diffs = []
        for color in COLORS:
            cr, cg, cb = color
            color_diff = sqrt(abs(r - cr)**2 + abs(g - cg)**2 + abs(b - cb)**2)
            color_diffs.append((color_diff, color))
        return min(color_diffs)[1]

    def _load_images(self, images, single=False) -> list:
        if single:
            return Image.open(self.kmz_zip.open(ZIP_KMZ_IMG_FOLDER+"/"+images))
        else:
            if images:
                kmz_imgs = [Image.open(self.kmz_zip.open(ZIP_KMZ_IMG_FOLDER+"/"+image)) for image in images]
            else:
                kmz_imgs = [Image.open(self.kmz_zip.open(image)) for image in self.kmz_zip.namelist() if image.split("/")[0] == ZIP_KMZ_IMG_FOLDER]
            return kmz_imgs

    def _generate_image(self, images: list, fullvh=False, vertical=False, horizontal=False):
        if horizontal:
            widths, heights = zip(*(img.size for img in images))
            total_width = sum(widths)
            max_height = max(heights)

            new_image = Image.new('RGB', (total_width, max_height))
            x_offset = 0
            for img in images:
                new_image.paste(img, (x_offset,0))
                x_offset += img.size[0]

        elif vertical:
            widths, heights = zip(*(img.size for img in images))
            max_width = max(widths)
            total_height = sum(heights)

            new_image = Image.new('RGB', (max_width, total_height))
            y_offset = 0
            for img in images:
                new_image.paste(img, (0,y_offset))
                y_offset += img.size[1]
        elif fullvh:
            vertical_set = [self._generate_image(image, horizontal=True) for image in images]
            new_image = self._generate_image(vertical_set, vertical=True)

        return new_image

    def get_pollution(self, user_coords):
        item = self._find_coords_item(user_coords)
        image = self._load_images(item[1], single=True)
        img_ = self._find_coords_image(user_coords, item, image)
        print(item)

    def global_imager(self, ) -> None:
        globe_images = [self._load_images(matrix["image"].tolist()) for matrix in self.globe_matrix]
        self._generate_image(globe_images, fullvh=True).save(KMZ_GLOBAL_IMAGE)


if __name__ == "__main__":
    myloc = [52.379971, 4.8196657]

    kmz = KMZ()
    #kmz.global_imager()

    kmz.get_pollution(myloc)
