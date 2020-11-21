import glob, csv
import pandas as pd
from lxml import html
from zipfile import ZipFile
from PIL import Image

pd.options.mode.chained_assignment = None

ZIP_KML_DOC = "doc.kml"
CSV_KML_DOC = "kml_index.csv"
ZIP_KMZ_IMG_FOLDER = "files"

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
        self.df.sort_values(by='north', ascending=False, inplace = True)

    def load_images(self, images) -> list:
        if images:
            self.kmz_imgs = [Image.open(self.kmz_zip.open(ZIP_KMZ_IMG_FOLDER+"/"+image)) for image in images]
        else:
            self.kmz_imgs = [Image.open(self.kmz_zip.open(image)) for image in self.kmz_zip.namelist() if image.split("/")[0] == ZIP_KMZ_IMG_FOLDER]
        return self.kmz_imgs

    def imager(self, ) -> None:
        globe_matrix = []
        globe_images = []
        for i, row in self.df.iterrows():
            sub_df = self.df.loc[(self.df['north'] == row['north']) & (self.df['south'] == row['south'])]
            if sub_df.empty:
                continue
            else:
                sub_df.sort_values(by='west', inplace = True)
                sub_matrix = sub_df["image"].tolist()
                globe_matrix.append(sub_matrix)
                self.df.drop(sub_df.index, inplace = True)

                sub_images = self.load_images(sub_matrix)
                widths, heights = zip(*(img.size for img in sub_images))
                total_width = sum(widths)
                max_height = max(heights)

                sub_lat_img = Image.new('RGB', (total_width, max_height))
                x_offset = 0
                for img in sub_images:
                    sub_lat_img.paste(img, (x_offset,0))
                    x_offset += img.size[0]
                globe_images.append(sub_lat_img)


        widths, heights = zip(*(img.size for img in globe_images))
        max_width = max(widths)
        total_height = sum(heights)

        globe_image = Image.new('RGB', (max_width, total_height))
        y_offset = 0
        for img in globe_images:
            globe_image.paste(img, (0,y_offset))
            y_offset += img.size[1]
        globe_image.save('test.jpg')


if __name__ == "__main__":
    kmz = KMZ()
    kmz.indexer_csv()
    kmz.load_csv()
    #kmz.load_images()
    kmz.imager()
