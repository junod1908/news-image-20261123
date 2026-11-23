# news-image-20261123 -- "Sum up 23 November's world news in one image."
#
# A one-page broadsheet, "The World in One Day", for Monday 23 November
# 2026. The program draws the whole page itself with the Python 3.13
# standard library only: no network, no clock, no randomness, so two runs
# write byte-identical files.
#
# Layout, top to bottom (v2: bigger hero + solid map + larger index type):
#   * serif masthead naming the day: THE WORLD IN ONE DAY
#     / MONDAY, 23 NOVEMBER 2026
#   * three illustrated lead stories (Ukraine talks, COP31 fallout,
#     Asian markets) with large flat vector icons (72 px)
#   * a solid-fill world map with big numbered red pins 1-15 for the
#     top stories, dots for every other story's place, and small
#     continent labels
#   * a UTC timeline strip
#   * 12 numbered top-story cards in two columns
#   * "ALSO ON MONDAY": 33 more stories as a numbered index in 3
#     columns, numbers in reading order (left to right, top to
#     bottom), set in BODY type scaled 1.25x; TONIGHT / TODAY agenda
#     items carry a navy badge and a gold tint so they cannot be
#     mistaken for the DATE CHECK box
#   * a DATE CHECK box listing the weekend stories deliberately left out
#
# 48 stories in all: 37 from the research team's date-audited list plus
# 11 more the builder verified against primary sources the same way
# (see the audit file's section G). Every story happened, or was first
# reported, on Monday 23 November 2026 in some time zone. Weekend events
# recycled by Monday digests were left out -- the COP31 collapse itself
# was Sunday, so only its Monday fallout is in; the Nikkei's 5% fall was
# Friday (Tokyo was closed Monday); the Skubal, Larkin, Democrats and
# Riemann stories all broke Friday or Sunday. Agenda items (Brazil's
# fiscal vote, Monday Night Football, the RSM Classic final, the turkey
# pardon vote) are labelled TONIGHT / TODAY, never shown as results.
#
# Every word on the page is set in type by this program from the bitmap
# fonts in assets/font.bin (DejaVu glyphs, rendered at build time by
# gen_font_ni23.py, which lives outside this repository).
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
LAND_FILL = (133, 158, 186)
GOLD = (219, 166, 66)
RED = (178, 34, 24)
MUTED = (110, 104, 90)
HAIRLINE = (219, 212, 194)
WHITE = (255, 255, 255)
TINT_GOLD = (238, 228, 210)
TINT_GREEN = (216, 228, 214)
TINT_BLUE = (220, 228, 236)
SLATE = (84, 96, 110)

# ---------------------------------------------------------------- copy
TITLE = "THE WORLD IN ONE DAY"
DATE = "MONDAY, 23 NOVEMBER 2026"
TIMELINE = ("TIMELINE (UTC)  -  02:40 VANUATU QUAKE  -  07:00 BRUSSELS "
            "AIRSPACE SHUT  -  09:00 EUROZONE PMI 51.7  -  09:30 UK PMI 52.3")
TOP_LABEL = "TOP STORIES"
ALSO_LABEL = "ALSO ON MONDAY - 33 MORE STORIES (48 IN ALL)"
DATECHECK_1 = ("DATE CHECK - NOT TODAY: COP31 FAILED SUN 22 - EL CHAPO "
               "FRI 21 - SHENZHEN THU 19 - NWSL SAT 21 - NIKKEI -5% FRI 20")
DATECHECK_2 = ("Every story above happened, or was first reported, "
               "on Monday 23 November 2026.")

# (num, headline, detail, lon, lat, dx, dy, kind, region)
# kind: "lead" (1-3), "card" (4-15), "list" (16-48).
# region is only used for list items, to group them into sections.
# Map offsets (dx, dy) separate pins/dots that would sit on each other.
STORIES = [
    # -- Leads ---------------------------------------------------------
    (1, "UKRAINE PEACE TALKS END IN DEADLOCK",
     "US offers NATO-style guarantees; January target",
     54, 24, 10, -8, "lead", None),
    (2, "COP31 FALLOUT: BLAME GAME BEGINS",
     "Talks ended Sunday; blame game starts Monday",
     149, -35, 0, 0, "lead", None),
    (3, "ASIAN MARKETS EXTEND LOSSES ON AI FEARS",
     "Kospi -5%, Taiex -6.2%; Tokyo closed for holiday",
     127, 37, 0, 0, "lead", None),
    # -- Top-story cards -----------------------------------------------
    (4, "NVIDIA SURGES 8% AFTER TRUMP BACKS HUANG",
     "Shares jump Monday; Trump post came Sunday",
     -74, 41, 0, 0, "card", None),
    (5, "ANTHROPIC REBOUNDS 3% AFTER FRIDAY FALL",
     "Stock near $91.50 after $81.3B IPO",
     -74, 41, 20, -14, "card", None),
    (6, "SOUTH KOREA RESHUFFLES FOREIGN, SPY CHIEFS",
     "First woman to lead NIS; Lee names new team",
     127, 37, 24, 14, "card", None),
    (7, "UKRAINE SINKS RUSSIAN WARSHIP MERKURY OFF LIBYA",
     "Zelenskyy: Sunday strike sank corvette Merkury",
     20, 32, 0, 0, "card", None),
    (8, "KYIV REGION DEATH TOLL RISES TO 15",
     "Dymer toll climbs Monday; boy, 7, pulled alive",
     30, 51, 16, -12, "card", None),
    (9, "SAUDI STRIKES HIT HODEIDA, FOUR KILLED",
     "Telecom building hit; 18 wounded",
     43, 15, 0, 0, "card", None),
    (10, "UN AND US CONDEMN KHARTOUM DRONE STRIKE",
     "Three UN staff hurt; UN building damaged",
     33, 16, 0, 0, "card", None),
    (11, "THAILAND-CAMBODIA CEASEFIRE HOLDS",
     "Phnom Penh confirms calm Monday morning",
     105, 12, 0, 0, "card", None),
    (12, "INDIA AND NEW ZEALAND DRAW FIRST TEST",
     "NZ 239/5 bat out 120 overs on Day 5",
     175, -41, 0, 0, "card", None),
    (13, "BELGIUM STRIKE GROUNDS 429 BRUSSELS FLIGHTS",
     "Airspace shut 07:00-21:00; 59,500 hit",
     4, 51, 0, 0, "card", None),
    (14, "TAIWAN TIGHTENS SHORT-SELLING RULES",
     "No shorts below close; margin up to 150%",
     121, 25, -14, 10, "card", None),
    (15, "TATA STEEL BUYS 26% OF APL APOLLO FOR $1.67B",
     "Steel-pipe maker APL Apollo; shares fall in both",
     73, 19, 0, 0, "card", None),
    # -- Also on Monday (numbered index, grouped by region) ------------
    (16, "GOLD HOLDS ABOVE $3,600; BITCOIN REBOUNDS", "",
     0, 51, 0, 0, "list", "GLOBAL & SPORT"),
    (17, "INDONESIA CONFIRMS 24 DEAD IN FACTORY FIRE", "",
     106, -6, 0, 0, "list", "ASIA"),
    (18, "MAGNITUDE 6.5 QUAKE JOLTS VANUATU REGION", "",
     167, -16, 0, 0, "list", "OCEANIA"),
    (19, "CALIFORNIA BRACES FOR RECORD KING TIDES", "",
     -122, 38, 0, 0, "list", "NORTH AMERICA"),
    (20, "OXFAM: GAZA CONTAMINATION COVERS 99% OF LAND", "",
     34, 31, 0, 0, "list", "MIDDLE EAST & AFRICA"),
    (21, "MACRON UNVEILS 14.9B EUROS AT CHOOSE FRANCE", "",
     1, 44, 0, 0, "list", "EUROPE"),
    (22, "AUSTRALIA FREEZES MEDICINE SCRIPTS AT $25", "",
     149, -35, 6, 4, "list", "OCEANIA"),
    (23, "AUSTRALIA PASSES CONTROVERSIAL DEFENCE BILL", "",
     149, -35, -6, -4, "list", "OCEANIA"),
    (24, "TAYLOR OVERTAKES ALBANESE AS PREFERRED PM", "",
     149, -35, 6, -6, "list", "OCEANIA"),
    (25, "INDIA COURT WEIGHS BS-VI-ONLY RULE FOR DELHI", "",
     77, 29, 0, 0, "list", "ASIA"),
    (26, "TONIGHT: BRAZIL HOUSE VOTES LULA FISCAL BILL", "",
     -48, -16, 0, 0, "list", "LATIN AMERICA"),
    (27, "LULA WEIGHS BILL TO CAP PUBLIC SALARIES", "",
     -48, -16, 7, 5, "list", "LATIN AMERICA"),
    (28, "SISI HOSTS IRAQI PM IN CAIRO", "",
     31, 30, 0, 0, "list", "MIDDLE EAST & AFRICA"),
    (29, "AMAZON LEO LAUNCH SCRUBBED, PUSHED TO TUESDAY", "",
     -53, 5, 0, 0, "list", "GLOBAL & SPORT"),
    (30, "OPENAI OPENS 50,000 FREE GRANTS FOR SCIENTISTS", "",
     -122, 38, 7, -5, "list", "NORTH AMERICA"),
    (31, "POPE MEETS CYCLING LEGENDS AT VATICAN", "",
     12, 42, 0, 0, "list", "EUROPE"),
    (32, "ONTARIO GIVES TORONTO $29M FOR CROSSING GUARDS", "",
     -79, 44, 0, 0, "list", "NORTH AMERICA"),
    (33, "ALCARAZ ARRIVES IN BOLOGNA FOR DAVIS CUP", "",
     11, 44, 0, 0, "list", "EUROPE"),
    (34, "UK SNOOKER QUALIFYING CONTINUES IN LEICESTER", "",
     -1, 53, 0, 0, "list", "EUROPE"),
    (35, "TONIGHT: BENGALS FACE COMMANDERS ON MONDAY NIGHT", "",
     -77, 39, 0, 0, "list", "NORTH AMERICA"),
    (36, "TODAY: RSM CLASSIC FINAL MOVES TO MONDAY", "",
     -81, 31, 0, 0, "list", "NORTH AMERICA"),
    (37, "TURKEY PARDON VOTE OPENS MONDAY", "",
     -77, 39, -7, 5, "list", "NORTH AMERICA"),
    (38, "UK PMI HOLDS AT 52.3; FACTORIES HIT 27-MONTH HIGH", "",
     0, 51, 14, -14, "list", "EUROPE"),
    (39, "EUROZONE PMI UNCHANGED AT 51.7", "",
     4, 51, 24, 12, "list", "EUROPE"),
    (40, "BURNHAM TELLS MPS EU DEAL IS 'LANDMARK'", "",
     0, 51, -16, 8, "list", "EUROPE"),
    (41, "ECB'S SIMKUS: DECEMBER HIKE MAY NOT BE ENOUGH", "",
     16, 48, 0, 0, "list", "EUROPE"),
    (42, "GERMAN PMI HITS 4 1/2-YEAR HIGH AT 55", "",
     13, 52, 0, 0, "list", "EUROPE"),
    (43, "LONDON SHARES REBOUND FROM 5-MONTH LOW", "",
     0, 51, 26, 14, "list", "EUROPE"),
    (44, "NEPAL PM VISITS INDIA; $1.63B AID ANNOUNCED", "",
     77, 29, 7, -5, "list", "ASIA"),
    (45, "S. KOREA EXPORTS NEARLY DOUBLE IN EARLY NOV", "",
     127, 37, -12, -8, "list", "ASIA"),
    (46, "BANDA SEA SHAKEN BY M5.4 QUAKE", "",
     130, -6, 0, 0, "list", "ASIA"),
    (47, "SEOUL READIES STABILISATION FUND", "",
     127, 37, 12, -10, "list", "ASIA"),
    (48, "EGYPT HOSTS GLOBAL SOCIAL PROTECTION FORUM", "",
     32, 30, 7, -4, "list", "MIDDLE EAST & AFRICA"),
]

# (Index items are shown in numeric reading order, row-major across
# three columns; the region field is kept only as data, no longer
# used to group the index into sections.)
# ---------------------------------------------------------------- dot map
# Coarse continent outlines as (lon, lat) polygons, equirectangular.
# Good enough for a dot map at 8 px spacing; the numbered pins are what
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

# Map geometry: lon -180..180 -> x 24..1000, lat 78..-58 -> y 196..284.
MAP_X0, MAP_X1 = 24, 1000
MAP_Y0, MAP_Y1 = 196, 284
MAP_LAT_TOP, MAP_LAT_BOT = 78, -58

# Small continent labels (lon, lat) -- placed clear of the pins.
MAP_LABELS = [
    ("NORTH AMERICA", -120, 55),
    ("SOUTH AMERICA", -68, -40),
    ("EUROPE", -15, 50),
    ("AFRICA", 20, -5),
    ("ASIA", 95, 65),
    ("AUSTRALIA", 134, -25),
]


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
def fill_poly(cv, pts, color):
    """Even-odd scanline fill of a pixel polygon (continent outlines)."""
    if len(pts) < 3:
        return
    min_y = min(p[1] for p in pts)
    max_y = max(p[1] for p in pts)
    n = len(pts)
    for yy in range(min_y, max_y + 1):
        xs = []
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if (y1 <= yy < y2) or (y2 <= yy < y1):
                xs.append(x1 + (yy - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for j in range(0, len(xs) - 1, 2):
            x0 = int(xs[j])
            x1 = int(xs[j + 1])
            if x1 >= x0:
                cv.fill_rect(x0, yy, x1 - x0 + 1, 1, color)


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


def wrap_lines(font, text, max_w, max_lines=2):
    """Greedy word wrap; drops words past max_lines (callers check)."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if font.width_of(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
            if len(lines) == max_lines:
                return lines, False
    if cur:
        lines.append(cur)
    return lines, len(lines) <= max_lines


def wrap_lines_scaled(fonts, font_name, text, max_ws, scale, max_lines=2):
    """Greedy word wrap at a fractional scale; max_ws is a per-line
    width list (first line may be narrower, e.g. behind a badge)."""
    font = fonts[font_name]
    if isinstance(max_ws, (int, float)):
        max_ws = [max_ws] * max_lines

    def w(t):
        return sum(max(1, int(round(font.glyphs.get(ord(c), (0, b""))[0] * scale)))
                   for c in t)

    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        limit = max_ws[min(len(lines), len(max_ws) - 1)]
        if w(trial) <= limit or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
            if len(lines) == max_lines:
                return lines, False
    if cur:
        lines.append(cur)
    return lines, len(lines) <= max_lines


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

    def width_scaled(self, fonts, font_name, text, scale, tracking=0):
        """Pixel width of text drawn with draw_text_scaled (same rounding)."""
        font = fonts[font_name]
        total = sum(max(1, int(round(font.glyphs.get(ord(ch), (0, b""))[0] * scale)))
                    for ch in text)
        return total + int(round(tracking * scale)) * max(0, len(text) - 1)

    def draw_text_scaled(self, fonts, font_name, x, baseline, text, color, scale, tracking=0):
        """Draw bitmap text scaled by a fractional factor with
        nearest-neighbour sampling (keeps the stdlib-only, deterministic
        renderer; used for the 1.25x index type and the big pin numbers)."""
        font = fonts[font_name]
        top = baseline - int(round(font.ascent * scale))
        pen = x
        step = int(round(tracking * scale))
        for ch in text:
            glyph = font.glyphs.get(ord(ch))
            if glyph is None:
                continue
            advance, bits = glyph
            gw = max(1, int(round(advance * scale)))
            gh = max(1, int(round(font.height * scale)))
            stride = (advance + 7) // 8
            for dy in range(gh):
                sy = min(font.height - 1, int(dy / scale))
                chunk = bits[sy * stride:(sy + 1) * stride]
                if not any(chunk):
                    continue
                yy = top + dy
                if yy < 0 or yy >= self.h:
                    continue
                for dx in range(gw):
                    sx = min(advance - 1, int(dx / scale))
                    if chunk[sx // 8] & (0x80 >> (sx % 8)):
                        self.set_px(pen + dx, yy, color)
            pen += gw + step

    def draw_text_scaled_centered(self, fonts, font_name, cx, baseline, text, color, scale, tracking=0):
        w = self.width_scaled(fonts, font_name, text, scale, tracking)
        self.draw_text_scaled(fonts, font_name, cx - w // 2, baseline, text, color, scale, tracking)


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


# ---------------------------------------------------------------- lead icons
# Small flat vector icons, drawn from rectangles and discs only.
# Every length scales with s (v1 used s = 52; v2 uses s = 72).
def icon_talks(cv, x, y, s):
    k = s / 52.0
    cv.fill_rect(x, y, s, s, TINT_BLUE)
    bar = max(2, round(4 * k))
    cv.fill_rect(x + round(6 * k), y + round(8 * k), s - round(12 * k), bar, NAVY)
    base = y + s - round(10 * k)
    for i, hgt in enumerate((18, 24, 20)):
        bx = x + round(10 * k) + i * round(14 * k)
        cv.fill_rect(bx, base - round(hgt * k), round(8 * k), round(hgt * k), NAVY)
    cv.fill_rect(x + round(6 * k), base, s - round(12 * k), bar, NAVY)


def icon_climate(cv, x, y, s):
    k = s / 52.0
    cv.fill_rect(x, y, s, s, TINT_GREEN)
    cv.fill_rect(x + round(8 * k), y + round(28 * k), round(22 * k), s - round(34 * k), SLATE)
    cv.fill_rect(x + round(32 * k), y + round(14 * k), round(6 * k), s - round(20 * k), SLATE)
    cv.disc(x + round(35 * k), y + round(10 * k), max(2, round(3 * k)), MUTED)
    cv.disc(x + round(39 * k), y + round(5 * k), max(2, round(3 * k)), MUTED)
    cv.disc(x + round(44 * k), y + round(10 * k), max(2, round(4 * k)), GOLD)


def icon_markets(cv, x, y, s):
    k = s / 52.0
    cv.fill_rect(x, y, s, s, TINT_GOLD)
    base = y + s - round(10 * k)
    cv.fill_rect(x + round(8 * k), base, s - round(16 * k), max(2, round(2 * k)), NAVY)
    for i, hgt in enumerate((30, 20, 12)):
        bx = x + round(12 * k) + i * round(12 * k)
        cv.fill_rect(bx, base - round(hgt * k), round(8 * k), round(hgt * k), RED)


LEAD_ICONS = {1: icon_talks, 2: icon_climate, 3: icon_markets}


# ---------------------------------------------------------------- build
def build():
    fonts = load_fonts(HERE / "assets" / "font.bin")
    cv = Canvas(W, H, PAPER)
    by_num = {s[0]: s for s in STORIES}

    # Masthead.
    cv.fill_rect(0, 0, W, 88, NAVY)
    cv.draw_text_centered(fonts, "MAST", W // 2, 52, TITLE, WHITE, tracking=1)
    cv.draw_text_centered(fonts, "DATE", W // 2, 80, DATE, GOLD)
    cv.fill_rect(0, 88, W, 4, RED)

    # Three illustrated leads (large 72 px icons).
    for i, num in enumerate((1, 2, 3)):
        _n, headline, detail, _lo, _la, _dx, _dy, _k, _r = by_num[num]
        x = 24 + i * 328
        y = 96
        cv.fill_rect(x, y + 4, 24, 24, RED)
        cv.draw_text_centered(fonts, "CAP", x + 12, y + 22, "%02d" % num, WHITE)
        LEAD_ICONS[num](cv, x + 30, y + 4, 72)
        lines, ok = wrap_lines(fonts["HEAD"], headline, 216, 2)
        if not ok:
            raise ValueError("lead headline overflows: %r" % headline)
        for li, line in enumerate(lines):
            cv.draw_text(fonts, "HEAD", x + 110, y + 22 + li * 17, line, INK)
        cv.draw_text(fonts, "SMALL", x, y + 88, detail, DETAIL)

    # Solid world map with big numbered pins 1-15 and dots for the rest.
    cv.fill_rect(24, 194, 976, 1, HAIRLINE)
    cv.fill_rect(24, 286, 976, 1, HAIRLINE)
    for poly in LAND:
        pts = [(int(lon_to_x(lon)), int(lat_to_y(lat))) for lon, lat in poly]
        fill_poly(cv, pts, LAND_FILL)
    for label, lon, lat in MAP_LABELS:
        cv.draw_text_centered(fonts, "SMALL", int(lon_to_x(lon)),
                              int(lat_to_y(lat)), label, NAVY)
    for num, _h, _d, lon, lat, dx, dy, _k, _r in STORIES:
        cx = int(lon_to_x(lon)) + dx
        cy = int(lat_to_y(lat)) + dy
        if num <= 15:
            cv.disc(cx, cy, 12, RED)
            cv.draw_text_scaled_centered(fonts, "PIN", cx, cy + 7,
                                         str(num), WHITE, 1.75)
        else:
            cv.disc(cx, cy, 3, RED)

    # UTC timeline strip.
    cv.draw_text_centered(fonts, "SMALL", W // 2, 296, TIMELINE, DETAIL)

    # Section label with hairline rules.
    def section_label(y, text):
        label_w = fonts["CAP"].width_of(text, tracking=2)
        mid = W // 2
        cv.draw_text_centered(fonts, "CAP", mid, y + 12, text, NAVY, tracking=2)
        cv.fill_rect(24, y + 6, mid - label_w // 2 - 16 - 24, 1, HAIRLINE)
        cv.fill_rect(mid + label_w // 2 + 16, y + 6,
                     1000 - (mid + label_w // 2 + 16), 1, HAIRLINE)

    section_label(304, TOP_LABEL)

    # Top-story cards, two columns: stories 4-9 left, 10-15 right.
    # Headlines are set with tracking -1 so the long warship headline
    # fits on one line without shrinking the type.
    row_y0 = 320
    row_h = 37
    for idx, num in enumerate(range(4, 16)):
        _n, headline, detail, _lo, _la, _dx, _dy, _k, _r = by_num[num]
        col = 0 if idx < 6 else 1
        row = idx if idx < 6 else idx - 6
        x = 24 if col == 0 else 524
        y = row_y0 + row * row_h
        if fonts["HEAD"].width_of(headline, tracking=-1) > 448:
            raise ValueError("card headline too wide: %r" % headline)
        if fonts["BODY"].width_of(detail) > 448:
            raise ValueError("card detail too wide: %r" % detail)
        cv.fill_rect(x, y + 3, 20, 20, RED)
        cv.draw_text_centered(fonts, "CAP", x + 10, y + 18, "%02d" % num, WHITE)
        cv.draw_text(fonts, "HEAD", x + 28, y + 15, headline, INK, tracking=-1)
        cv.draw_text(fonts, "BODY", x + 28, y + 30, detail, DETAIL)
        if row < 5:
            cv.fill_rect(x, y + 35, 476, 1, HAIRLINE)

    section_label(550, ALSO_LABEL)

    # Numbered index in reading order: row-major across 3 columns, so
    # the numbers run 16, 17, 18 across the top row, then 19, 20, 21,
    # and so on down to 48. Type is BODY scaled 1.25x (+25% on v1).
    # TONIGHT / TODAY agenda items get a navy badge and a gold tint,
    # visually separated from the DATE CHECK box at the foot.
    list_y = 568
    col_w = 314
    col_xs = [24, 24 + col_w + 16, 24 + 2 * (col_w + 16)]
    row_pitch = 37
    line_pitch = 18
    index_scale = 1.25
    list_items = sorted((s for s in STORIES if s[7] == "list"), key=lambda s: s[0])
    for pos, item in enumerate(list_items):
        num, headline = item[0], item[1]
        row, col = divmod(pos, 3)
        x = col_xs[col]
        y = list_y + row * row_pitch
        agenda = None
        for tag in ("TONIGHT:", "TODAY:"):
            if headline.startswith(tag):
                agenda = tag[:-1]
                headline = headline[len(tag):].strip()
                break
        text_x = x + 28
        if agenda:
            cv.fill_rect(x - 4, y - 2, col_w + 6, row_pitch + 2, TINT_GOLD)
            badge_w = fonts["CAP"].width_of(agenda) + 12
            cv.fill_rect(text_x, y + 1, badge_w, 18, NAVY)
            cv.draw_text_centered(fonts, "CAP", text_x + badge_w // 2,
                                  y + 15, agenda, WHITE)
            first_w = col_w - 28 - badge_w - 6
            lines, ok = wrap_lines_scaled(fonts, "BODY", headline,
                                          [first_w, col_w - 28],
                                          index_scale, 2)
            line_xs = [text_x + badge_w + 6, text_x]
        else:
            lines, ok = wrap_lines_scaled(fonts, "BODY", headline,
                                          col_w - 28, index_scale, 2)
            line_xs = [text_x, text_x]
        if not ok:
            raise ValueError("index item overflows two lines: #%d %r" % (num, headline))
        cv.draw_text(fonts, "CAP", x, y + 15, "%02d" % num, RED)
        for li, line in enumerate(lines):
            cv.draw_text_scaled(fonts, "BODY", line_xs[li], y + 15 + li * line_pitch,
                                line, INK, index_scale)

    # DATE CHECK box.
    if fonts["CAP"].width_of(DATECHECK_1) > 964:
        raise ValueError("DATE CHECK line too wide")
    cv.fill_rect(24, 984, 976, 1, NAVY)
    cv.fill_rect(24, 984, 1, 36, NAVY)
    cv.fill_rect(999, 984, 1, 36, NAVY)
    cv.fill_rect(24, 1019, 976, 1, NAVY)
    cv.draw_text(fonts, "CAP", 36, 997, DATECHECK_1, RED)
    cv.draw_text(fonts, "SMALL", 36, 1013, DATECHECK_2, DETAIL)

    return encode_png(cv)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = build()
    (OUT_DIR / "entry.png").write_bytes(data)


if __name__ == "__main__":
    main()
