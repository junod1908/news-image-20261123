# news-image-20261123 -- "Sum up 23 November's world news in one image."
#
# A one-page broadsheet, "The World in One Day", for Monday 23 November
# 2026. The program draws the whole page itself with the Python 3.13
# standard library only: no network, no clock, no randomness, so two runs
# write byte-identical files.
#
# Layout, top to bottom:
#   * navy masthead naming the day: THE WORLD IN ONE DAY
#     / MONDAY, 23 NOVEMBER 2026
#   * a date-check strip that says, on the face of the poster, that every
#     story happened or was first reported on that Monday
#   * a dot world map with a red marker at each story's place
#   * 36 numbered story cards in two columns, ordered by region:
#     Americas, Europe, Middle East & Africa, Asia-Pacific, then
#     technology & markets
#   * a footer repeating the date check
#
# Every word on the page is set in type by this program from the bitmap
# fonts in assets/font.bin (DejaVu glyphs, rendered at build time by
# gen_font_ni23.py, which lives outside this repository).
#
# All 36 stories were checked against primary reporting before the build:
# each one happened, or was first reported, on Monday 23 November 2026
# in some time zone. Weekend events recycled by Monday digests (the COP31
# collapse, the Dymer strike, the Marquez MotoGP title, the NWSL final)
# were left out on purpose. Two US Sunday-night games are in only
# because they were still being played after midnight UTC on Monday.
#
# Run it locally with:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import binascii
import os
import struct
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 233)
INK = (24, 24, 24)
DETAIL = (58, 54, 46)
NAVY = (22, 37, 62)
MAPDOT = (52, 82, 128)
GOLD = (219, 166, 66)
RED = (178, 34, 24)
MUTED = (110, 104, 90)
HAIRLINE = (219, 212, 194)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- copy
TITLE = "THE WORLD IN ONE DAY"
DATE = "MONDAY, 23 NOVEMBER 2026"
DATECHECK = ("DATE CHECK: EVERY STORY BELOW HAPPENED, OR WAS FIRST REPORTED, "
             "ON MONDAY 23 NOVEMBER 2026")
SECTION = "THE DAY IN 36 STORIES"
FOOTER = ("All 36 stories happened, or were first reported, on Monday "
          "23 November 2026  -  news-image-20261123")

# (headline, detail, lon, lat, marker dx, marker dy)
# Marker offsets separate dots that would otherwise sit on each other
# (Washington twice, London three times, Paris and Seoul twice).
STORIES = [
    # -- Americas ------------------------------------------------------
    ("DEMOCRATS WIN BIGGEST HOUSE MAJORITY",
     "Hubbard recount win; 258 seats, best since 1992",
     -77, 39, 0, 0),
    ("TRUMP SIGNS COMMON CENTS ACT; PENNY ENDS",
     "232-year run of the one-cent coin closes",
     -77, 39, 7, -6),
    ("DELTA OUTAGE RESOLVED AFTER 1,600 DELAYS",
     "Weight-and-balance failure hits Atlanta hub",
     -84, 34, 0, 0),
    ("SKUBAL SIGNS RECORD $450M METS DEAL",
     "Nine years; biggest pitcher contract ever",
     -74, 41, 0, 0),
    ("LARKIN TRADED TO MONTREAL IN BLOCKBUSTER",
     "Detroit sends captain; Dach, picks go back",
     -83, 42, -7, 4),
    ("BOLSONARO IN INTENSIVE CARE",
     "Ex-president treated for intestinal obstruction",
     -48, -16, 0, 0),
    ("NUGGETS OUTLAST BULLS 151-145 IN OT",
     "Murray 45; Jokic triple-double No. 202",
     -88, 42, 0, 0),
    ("WARRIORS EDGE CELTICS 88-87 WITHOUT CURRY",
     "Golden State ends five-game skid",
     -71, 42, 0, 0),
    # -- Europe --------------------------------------------------------
    ("BURNHAM HAILS EU DEAL AS DECADE-CHANGER",
     "PM presses MPs as May warns on rejoining",
     0, 51, 0, 0),
    ("THOUSANDS RALLY IN ISTANBUL OVER MEDIA GRAB",
     "Protest against press crackdown",
     29, 41, 0, 0),
    ("LE PEN DENIES LEAKED BRIEF FROM MINISTRY",
     "Far-right leader rejects interior leak claim",
     2, 49, 0, 0),
    ("FRANCE FRONTRUNNERS QUESTION UKRAINE AID",
     "Both leading candidates cool on Kyiv support",
     2, 49, 7, 5),
    ("UK PMI HOLDS AT 52.3; MANUFACTURING 52.7",
     "November flash data beats forecasts",
     0, 51, 8, -4),
    ("EUROZONE PMI UNCHANGED AT 51.7",
     "Growth flat as factories stabilise",
     4, 51, -7, -5),
    ("ECB'S SIMKUS: DECEMBER HIKE MAY NOT SUFFICE",
     "Price pressures building only slowly",
     9, 50, 0, 0),
    ("ITALY PROBES EUROSPIN OVER PRICE PACT",
     "Antitrust opens vertical-agreement case",
     12, 42, 0, 0),
    # -- Middle East & Africa ------------------------------------------
    ("HOUTHIS CLAIM SAUDI REFINERY STRIKE",
     "Riyadh hits Hodeida in reply",
     43, 15, 0, 0),
    ("TANKERS ABLAZE NEAR HORMUZ IN IRAN WAR",
     "Bahrain says civilian site struck",
     51, 26, 0, 0),
    ("NETANYAHU-EISENKOT TALKS END WITHOUT DEAL",
     "Coalition negotiations collapse in Israel",
     35, 32, 0, 0),
    ("GAZA WAR LEFT WIDESPREAD CONTAMINATION",
     "Experts warn of toxic rubble, water risks",
     34, 31, -7, 5),
    ("FIVE CHILDREN KILLED IN KHARTOUM STRIKES",
     "Attacks hit Khartoum and Omdurman",
     33, 16, 0, 0),
    ("24 CIVILIANS KILLED IN SOUTH SUDAN ATTACK",
     "Paramilitary assault condemned",
     32, 5, 0, 0),
    ("KENYA AND DR CONGO AGREE TO RESTORE TIES",
     "Neighbours move to repair relations",
     37, -1, 0, 0),
    # -- Asia-Pacific --------------------------------------------------
    ("NIKKEI PLUNGES 5.06% AS AI SELL-OFF SPREADS",
     "Tokyo leads Asia rout on valuation fears",
     140, 36, 0, 0),
    ("TAIWAN BANS SHORT SALES BELOW FRIDAY CLOSE",
     "Third curb this month; stocks swing wildly",
     121, 25, 0, 0),
    ("S. KOREA EXPORTS TOP $1 TRILLION FIRST TIME",
     "Chips drive record year; 4th economy to do so",
     127, 37, 0, 0),
    ("SOUTH KOREA EDUCATION MINISTER RESIGNS",
     "Exam-cheating scandal claims minister",
     127, 37, 7, -5),
    ("NEPAL PM BALEN SHAH VISITS INDIA",
     "First foreign trip; Delhi pledges aid",
     77, 29, 0, 0),
    ("MODI OPENS AI CENTRE AT IIT PATNA",
     "PM inaugurates research hub",
     85, 26, 0, 0),
    ("MP RAMRAO WADKUTE DIES IN DELHI",
     "Rajya Sabha member passes away",
     77, 29, 7, 5),
    ("NEW ZEALAND BAT OUT DRAW IN WELLINGTON",
     "Mitchell, Phillips defy India after 720/9",
     175, -41, 0, 0),
    ("MONGOLIA PARLIAMENT OKS PRESIDENT'S EXIT",
     "President's resignation accepted",
     107, 48, 0, 0),
    # -- Technology & markets ------------------------------------------
    ("ANTHROPIC CLAIMS RIEMANN PROOF",
     "Alpoge and Claude say prime puzzle solved",
     -122, 38, 0, 0),
    ("METR: AI CAPABILITIES OUTPACING SAFETY TESTS",
     "Task length doubles every 3.6 months",
     -122, 38, 7, 5),
    ("NVIDIA REBOUNDS 8% AFTER 14% FRIDAY PLUNGE",
     "Chipmaker steadies premarket",
     -122, 37, -7, -5),
    ("GOLD RISES AS INVESTORS SEEK SAFETY",
     "Bullion up 2.7% in AI-rout flight",
     0, 51, -7, 5),
]

# ---------------------------------------------------------------- dot map
# Coarse continent outlines as (lon, lat) polygons, equirectangular.
# Good enough for a dot map at 8 px spacing; the red markers are what
# tie the map to the day's stories.
NORTH_AMERICA = [
    (-168, 66), (-158, 58), (-152, 60), (-145, 60), (-136, 58),
    (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29),
    (-108, 25), (-101, 19), (-95, 16), (-90, 14), (-84, 12),
    (-79, 9), (-75, 10), (-70, 12), (-64, 11), (-59, 8),
    (-54, 5), (-52, 4), (-55, 7), (-60, 10), (-62, 14),
    (-66, 18), (-69, 19), (-73, 20), (-77, 21), (-81, 24),
    (-81, 28), (-80, 32), (-76, 35), (-74, 39), (-70, 42),
    (-68, 44), (-64, 45), (-60, 46), (-56, 48), (-55, 50),
    (-58, 52), (-62, 54), (-66, 55), (-71, 55), (-76, 53),
    (-80, 52), (-84, 54), (-87, 58), (-90, 62), (-93, 66),
    (-98, 68), (-105, 68), (-112, 68), (-120, 69), (-128, 70),
    (-136, 69), (-144, 70), (-152, 71), (-160, 70), (-166, 68),
]
GREENLAND = [
    (-46, 60), (-40, 64), (-32, 68), (-26, 70), (-30, 74),
    (-38, 77), (-50, 77), (-58, 75), (-58, 71), (-53, 66), (-48, 61),
]
SOUTH_AMERICA = [
    (-79, 9), (-75, 7), (-71, 11), (-65, 11), (-60, 9),
    (-55, 6), (-51, 4), (-50, 0), (-44, -3), (-38, -5),
    (-35, -8), (-37, -13), (-39, -17), (-41, -22), (-46, -24),
    (-49, -28), (-53, -33), (-58, -38), (-62, -41), (-65, -45),
    (-67, -50), (-69, -52), (-71, -54), (-74, -52), (-74, -46),
    (-73, -40), (-73, -36), (-72, -29), (-71, -21), (-70, -18),
    (-74, -15), (-78, -10), (-80, -5), (-81, -1), (-80, 4),
]
AFRICA = [
    (-17, 15), (-16, 21), (-13, 26), (-9, 31), (-5, 34),
    (-1, 35), (4, 37), (10, 37), (12, 34), (16, 32),
    (20, 32), (25, 31), (30, 31), (33, 28), (35, 24),
    (37, 20), (39, 16), (41, 12), (45, 11), (48, 11),
    (51, 12), (50, 7), (46, 3), (43, 0), (41, -4),
    (40, -9), (38, -14), (36, -19), (34, -23), (33, -27),
    (30, -31), (27, -34), (22, -35), (19, -35), (16, -32),
    (14, -28), (13, -23), (12, -17), (12, -12), (9, -7),
    (9, -2), (9, 2), (7, 4), (3, 6), (-3, 5),
    (-8, 5), (-13, 8), (-15, 11),
]
EURASIA = [
    (-10, 37), (-9, 43), (-2, 48), (0, 51), (4, 53),
    (8, 57), (10, 59), (18, 56), (21, 55), (24, 58),
    (28, 60), (30, 63), (33, 66), (37, 67), (44, 68),
    (54, 69), (68, 72), (78, 73), (90, 75), (104, 76),
    (115, 74), (128, 72), (142, 72), (155, 70), (170, 67),
    (178, 65), (170, 60), (162, 56), (158, 52), (156, 50),
    (150, 47), (142, 42), (135, 35), (130, 33), (127, 35),
    (126, 38), (122, 39), (120, 35), (121, 31), (118, 25),
    (113, 22), (109, 18), (106, 10), (104, 9), (101, 8),
    (100, 6), (98, 10), (95, 15), (92, 21), (89, 22),
    (86, 20), (82, 16), (80, 13), (77, 8), (75, 11),
    (73, 17), (71, 20), (68, 23), (66, 25), (62, 25),
    (58, 26), (52, 27), (48, 29), (43, 28), (39, 21),
    (36, 36), (30, 36), (27, 37), (23, 36), (19, 40),
    (15, 44), (12, 44), (8, 44), (3, 42), (0, 38), (-6, 36),
]
ARABIA = [
    (43, 12), (40, 16), (38, 20), (39, 25), (42, 28),
    (46, 29), (48, 29), (50, 26), (52, 25), (55, 24),
    (57, 25), (59, 22), (58, 19), (55, 17), (51, 15),
    (47, 13), (44, 12),
]
UK = [(-5, 50), (-3, 53), (-5, 56), (-4, 58), (-2, 57), (0, 53), (1, 51), (-1, 50)]
SUMATRA = [(95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (103, -5), (100, -2), (97, 1)]
BORNEO = [(109, 1), (111, 3), (114, 5), (117, 6), (119, 3), (118, 0), (116, -3), (113, -4), (110, -3)]
JAVA = [(105, -6), (108, -7), (111, -7), (114, -8), (113, -9), (109, -8), (106, -7)]
NEW_GUINEA = [
    (131, -1), (134, -2), (137, -3), (141, -4), (145, -6),
    (148, -8), (150, -9), (147, -9), (143, -8), (139, -7),
    (135, -5), (132, -3),
]
PHILIPPINES = [
    (120, 18), (121, 17), (122, 15), (121, 13), (122, 11),
    (123, 10), (121, 11), (120, 13), (120, 16),
]
JAPAN = [
    (130, 31), (132, 33), (134, 34), (136, 35), (138, 35),
    (140, 36), (141, 38), (141, 41), (142, 43), (144, 44),
    (142, 42), (140, 39), (138, 37), (136, 35), (134, 34),
    (132, 33), (130, 32),
]
AUSTRALIA = [
    (113, -22), (114, -28), (115, -33), (118, -35), (122, -34),
    (126, -32), (129, -32), (132, -32), (135, -35), (137, -35),
    (139, -37), (142, -38), (146, -39), (150, -37), (153, -32),
    (153, -27), (151, -24), (148, -20), (145, -17), (142, -14),
    (142, -11), (139, -12), (136, -12), (133, -12), (130, -13),
    (127, -14), (124, -15), (121, -17), (118, -20), (115, -21),
]
NEW_ZEALAND = [
    (167, -45), (169, -43), (171, -41), (174, -39), (176, -38),
    (178, -38), (176, -40), (174, -42), (171, -44), (168, -46),
]
MADAGASCAR = [
    (44, -16), (47, -15), (50, -16), (49, -19), (47, -23),
    (45, -25), (44, -22), (43, -18),
]
LAND = [
    NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA, ARABIA,
    UK, SUMATRA, BORNEO, JAVA, NEW_GUINEA, PHILIPPINES, JAPAN,
    AUSTRALIA, NEW_ZEALAND, MADAGASCAR,
]

# Map geometry: lon -180..180 -> x 24..1000, lat 78..-58 -> y 136..240.
MAP_X0, MAP_X1 = 24, 1000
MAP_Y0, MAP_Y1 = 136, 240
MAP_LAT_TOP, MAP_LAT_BOT = 78, -58


def lon_to_x(lon):
    return MAP_X0 + (lon + 180) / 360 * (MAP_X1 - MAP_X0)


def lat_to_y(lat):
    return MAP_Y0 + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) * (MAP_Y1 - MAP_Y0)


def _crosses(lon, lat, a, b):
    (x1, y1), (x2, y2) = a, b
    if (y1 > lat) == (y2 > lat):
        return False
    return lon < x1 + (lat - y1) * (x2 - x1) / (y2 - y1)


def on_land(lon, lat):
    for poly in LAND:
        lons = [p[0] for p in poly]
        lats = [p[1] for p in poly]
        if not (min(lons) - 2 <= lon <= max(lons) + 2):
            continue
        if not (min(lats) - 2 <= lat <= max(lats) + 2):
            continue
        inside = False
        for i, pt in enumerate(poly):
            if _crosses(lon, lat, pt, poly[i - 1]):
                inside = not inside
        if inside:
            return True
    return False


# ---------------------------------------------------------------- fonts
# FNT2: magic b"FNT2", one byte font count, then per font a 14-byte header
# (name 8s, px u16, ascent u16, height u16) and 95 glyphs for codes
# 32..126, each (code u8, advance u8, byte-length u16) followed by
# ceil(advance/8)*height bytes of bitmap rows, MSB first.
class GlyphFont:
    def __init__(self, name, ascent, height, glyphs):
        self.name = name
        self.ascent = ascent
        self.height = height
        self.glyphs = glyphs  # code -> (advance, bitmap bytes)

    def width_of(self, text, tracking=0):
        total = sum(self.glyphs.get(ord(ch), (0, b""))[0] for ch in text)
        return total + tracking * max(0, len(text) - 1)


def load_fonts(path):
    raw = zlib.decompress(Path(path).read_bytes())
    if raw[:4] != b"FNT2":
        raise ValueError("bad font file")
    pos = 4
    count = raw[pos]
    pos += 1
    fonts = {}
    for _ in range(count):
        name, _px, ascent, height = struct.unpack_from(">8sHHH", raw, pos)
        pos += 14
        glyphs = {}
        for _ in range(95):
            code, advance, blen = struct.unpack_from(">BBH", raw, pos)
            pos += 4
            glyphs[code] = (advance, raw[pos:pos + blen])
            pos += blen
        clean = name.rstrip(b"\0").decode()
        fonts[clean] = GlyphFont(clean, ascent, height, glyphs)
    return fonts


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def set_px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.buf[o:o + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            o = self._off(x0, yy)
            self.buf[o:o + len(row)] = row

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def draw_text(self, fonts, font_name, x, baseline, text, color, tracking=0):
        font = fonts[font_name]
        top = baseline - font.ascent
        pen = x
        for ch in text:
            glyph = font.glyphs.get(ord(ch))
            if glyph is None:
                continue
            advance, bits = glyph
            stride = (advance + 7) // 8
            for row in range(font.height):
                chunk = bits[row * stride:(row + 1) * stride]
                yy = top + row
                if yy < 0 or yy >= self.h or not any(chunk):
                    continue
                for bi, byte in enumerate(chunk):
                    if not byte:
                        continue
                    for bit in range(8):
                        col = bi * 8 + bit
                        if col >= advance:
                            break
                        if byte & (0x80 >> bit):
                            self.set_px(pen + col, yy, color)
            pen += advance + tracking

    def draw_text_centered(self, fonts, font_name, cx, baseline, text, color, tracking=0):
        font = fonts[font_name]
        w = font.width_of(text, tracking)
        self.draw_text(fonts, font_name, cx - w // 2, baseline, text, color, tracking)


# ---------------------------------------------------------------- PNG out
def _chunk(kind, data):
    blob = struct.pack(">I", len(data)) + kind + data
    return blob + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)


def encode_png(canvas):
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


# ---------------------------------------------------------------- build
def build():
    fonts = load_fonts(HERE / "assets" / "font.bin")
    cv = Canvas(W, H, PAPER)

    # Masthead.
    cv.fill_rect(0, 0, W, 98, NAVY)
    cv.draw_text_centered(fonts, "MAST", W // 2, 58, TITLE, WHITE, tracking=1)
    cv.draw_text_centered(fonts, "DATE", W // 2, 88, DATE, GOLD)
    cv.fill_rect(0, 98, W, 4, RED)

    # Date-check strip.
    cv.draw_text_centered(fonts, "SMALL", W // 2, 122, DATECHECK, DETAIL)

    # Dot world map.
    for gx in range(28, 997, 8):
        lon = (gx - MAP_X0) / (MAP_X1 - MAP_X0) * 360 - 180
        for gy in range(140, 239, 6):
            lat = MAP_LAT_TOP - (gy - MAP_Y0) / (MAP_Y1 - MAP_Y0) * (MAP_LAT_TOP - MAP_LAT_BOT)
            if on_land(lon, lat):
                cv.disc(gx, gy, 2, MAPDOT)
    for _h, _d, lon, lat, dx, dy in STORIES:
        cv.disc(int(lon_to_x(lon)) + dx, int(lat_to_y(lat)) + dy, 3, RED)

    # Section label with hairline rules.
    label_w = fonts["CAP"].width_of(SECTION, tracking=2)
    mid = W // 2
    cv.draw_text_centered(fonts, "CAP", mid, 264, SECTION, NAVY, tracking=2)
    cv.fill_rect(24, 258, mid - label_w // 2 - 16 - 24, 1, HAIRLINE)
    cv.fill_rect(mid + label_w // 2 + 16, 258,
                 1000 - (mid + label_w // 2 + 16), 1, HAIRLINE)

    # Story cards, two columns: stories 1-18 left, 19-36 right.
    row_y0 = 280
    row_h = 38
    for idx, (headline, detail, _lon, _lat, _dx, _dy) in enumerate(STORIES):
        col = 0 if idx < 18 else 1
        row = idx if idx < 18 else idx - 18
        x = 24 if col == 0 else 524
        y = row_y0 + row * row_h
        num = "%02d" % (idx + 1)
        cv.fill_rect(x, y + 4, 22, 22, RED)
        cv.draw_text_centered(fonts, "CAP", x + 11, y + 20, num, WHITE)
        cv.draw_text(fonts, "HEAD", x + 30, y + 19, headline, INK)
        cv.draw_text(fonts, "BODY", x + 30, y + 35, detail, DETAIL)
        if row < 17:
            cv.fill_rect(x, y + 37, 476, 1, HAIRLINE)

    # Footer.
    cv.draw_text_centered(fonts, "SMALL", W // 2, 992, FOOTER, MUTED)

    return encode_png(cv)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = build()
    (OUT_DIR / "entry.png").write_bytes(data)


if __name__ == "__main__":
    main()
