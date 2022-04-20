from math import sqrt

COLORS = [
    (255, 255, 255),  # 0 white
    (225, 190, 255),  # 1 light purple
    (225, 110, 255),  # 2 purple
    (230, 0, 0),      # 3 red
    (255, 80, 0),     # 4 orange
    (255, 255, 0),    # 5 yellow
    (50, 140, 0),     # 6 green
    (0, 150, 210),    # 7 light blue
    (0, 75, 180),     # 8 blue
    (0, 35, 115),     # 9 dark blue
    (128, 128, 128),  # 10 light grey
    (77, 77, 77),     # 11 dark grey
    #(0, 0, 0),        # 12 black
]

HI_P = COLORS[:7]
LO_P = COLORS[7:10] # skipped black since it's usually ocean

def find_pollution_coords(user_coords: list, edges: list, image: bytes) -> list:
    width, height = image.size
    wpx = int(height * (user_coords[1] - edges[3]) / (edges[2] - edges[3]))
    hpx = width - int(width * (user_coords[0] - edges[1]) / (edges[0] - edges[1]))

    pixelmap = image.load()

    ilev = 0
    cus = [] # closest_unique_spots
    indexed_colors = []
    stopper = True
    while not len(cus) == len(LO_P) and stopper:
        ilev += 1
        layer = []
        # top row
        wpos = wpx - ilev
        for i in range(hpx - ilev, hpx + ilev):
            layer.append([wpos, i])
        # right column
        hpos = hpx + ilev
        for i in range(wpx - ilev, wpx + ilev):
            layer.append([i, hpos])
        # bottom row
        wpos = wpx + ilev
        for i in range(hpx - ilev + 1, hpx + ilev + 1):
            layer.append([wpos, i])
        # left column
        hpos = hpx - ilev
        for i in range(wpx - ilev + 1, wpx + ilev + 1):
            layer.append([i, hpos])

        for px in layer:
            try:
                color = _closest_color(pixelmap[px[0], px[1]])
            except IndexError:
                stopper = False
                break
            if not color in indexed_colors and color in LO_P:
                cus.append(_matrix_geo_coords(width, height, edges, px))
                indexed_colors.append(color)

    return cus

def _matrix_geo_coords(width: int, height: int, edges: list, matrix_coords: list) -> tuple:
    return (
        edges[0] - ((edges[0] - edges[1]) / width * matrix_coords[1]), # latitude
        edges[3] + ((edges[2] - edges[3]) / height * matrix_coords[0]) # longitude
    )

def _closest_color(rgb: list) -> tuple:
    r, g, b = rgb
    color_diffs = []
    for color in COLORS:
        cr, cg, cb = color
        color_diff = sqrt(abs(r - cr) ** 2 + abs(g - cg) ** 2 + abs(b - cb) ** 2)
        color_diffs.append((color_diff, color))
    return min(color_diffs)[1]
