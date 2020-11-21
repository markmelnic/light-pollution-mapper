import glob, csv
from lxml import html
from zipfile import ZipFile

ZIP_KML_DOC = "doc.kml"

class KMZ:
    def __init__(self) -> None:
        self.kmz_file = glob.glob("*.kmz")[0]
        self.kmz_zip = ZipFile(self.kmz_file, "r")
        self.kml_file = self.kmz_zip.open(ZIP_KML_DOC, "r").read()

    def indexer_csv(self,):
        kml_content = html.fromstring(self.kml_file)
        with open("kml_index.csv", "w", newline="") as kml_csv:
            kml_csv_writer = csv.writer(kml_csv)
            kml_csv_writer.writerow(
                ["image", "draw_order", "north", "south", "east", "west", "rotation"]
            )
            for item in kml_content.cssselect("Document GroundOverlay"):
                image = item.cssselect("name")[0].text_content()
                draw_order = item.cssselect("drawOrder")[0].text_content()
                coords = item.cssselect("LatLonBox")[0]
                north = coords.cssselect("north")[0].text_content()
                south = coords.cssselect("south")[0].text_content()
                east = coords.cssselect("east")[0].text_content()
                west = coords.cssselect("west")[0].text_content()
                rotation = coords.cssselect("rotation")[0].text_content()
                # print([image, draw_order, north, south, east, west, rotation])
                kml_csv_writer.writerow(
                    [image, draw_order, north, south, east, west, rotation]
                )

if __name__ == "__main__":
    kmz = KMZ()
    kmz.indexer_csv()
