import glob, csv
import pandas as pd
from lxml import html
from zipfile import ZipFile
from PIL import Image

ZIP_KML_DOC = "doc.kml"
CSV_KML_DOC = "kml_index.csv"

class KMZ:
    def __init__(self) -> None:
        self.kmz_file = glob.glob("*.kmz")[0]
        self.kmz_zip = ZipFile(self.kmz_file, "r")
        self.kml_file = self.kmz_zip.open(ZIP_KML_DOC, "r").read()

    def indexer_csv(self,) -> None:
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

    def load_csv(self, ) -> None:
        self.df = pd.read_csv(CSV_KML_DOC)

    def load_images(self, ) -> None:
        self.kmz_imgs = [Image.open(self.kmz_zip.open(image)) for image in self.kmz_zip.namelist() if image.split("/")[0] == "files"]

    def imager(self, ) -> None:
        widths, heights = zip(*(img.size for img in self.kmz_imgs))

if __name__ == "__main__":
    kmz = KMZ()
    #kmz.indexer_csv()
    #kmz.load_csv()
    #kmz.imager()
    kmz.load_images()
