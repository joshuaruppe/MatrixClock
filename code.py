import random
import time
import displayio
import terminalio
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_display_text import label

# =============================================================================
# Configuration, Constants & Variables
# =============================================================================

WIDTH = 64
HEIGHT = 32

TIME_WIDTH = 20 
DIVIDER_WIDTH = 1
MATRIX_X_OFFSET = TIME_WIDTH + DIVIDER_WIDTH

COLUMNS_WIDTH = WIDTH - TIME_WIDTH - DIVIDER_WIDTH
COLUMN_HEIGHT = HEIGHT

NUM_COLUMNS = COLUMNS_WIDTH
UPDATE_INTERVAL = 0.05

MATRIX_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()<>?[]{}"
CHAR_PROBABILITY = 0.2

SYNC_INTERVAL = 6 * 60 * 60

last_minute = None
last_sync_time = time.time()

# =============================================================================
# Helper Functions
# =============================================================================

def create_palette():
    palette = displayio.Palette(256)
    for i in range(256):
        if i < 200:
            green = int(100 + (i / 200) * 155)
            palette[i] = (0, green, 0)
        else:
            green = min(255, int(100 + ((i - 200) / 56) * 155))
            blue = min(255, int((i - 200) * 5))
            red = min(255, int((i - 200) * 3))
            palette[i] = (red, green, blue)
    palette[0] = (0, 0, 0)
    return palette

def create_column():
    return {
        "y": random.randint(-COLUMN_HEIGHT, 0),
        "speed": random.randint(1, 3),
        "trail_length": random.randint(3, 6),
        "trail": []
    }

def update_columns(columns):
    for column in columns:
        column["y"] += column["speed"]

        if column["y"] >= COLUMN_HEIGHT:
            column["y"] = random.randint(-COLUMN_HEIGHT // 2, -1)
            column["trail"] = []
            column["trail_length"] = random.randint(3, 6)

        if random.random() < CHAR_PROBABILITY:
            new_char = random.choice(MATRIX_CHARS)
        else:
            new_char = " "

        column["trail"].insert(0, new_char)

        if len(column["trail"]) > column["trail_length"]:
            column["trail"].pop()

def draw_columns(bitmap, columns):
    for col_index, column in enumerate(columns):
        x = col_index
        for trail_index, char in enumerate(column["trail"]):
            y = column["y"] - trail_index
            if 0 <= y < COLUMN_HEIGHT:
                if char == " ":  
                    bitmap[x, y] = 0
                else:
                    if trail_index == 0:
                        color_index = random.randint(240, 255)  
                    else:
                        color_index = random.randint(100, 200)
                    bitmap[x, y] = color_index

# =============================================================================
# Main Program
# =============================================================================

print("Starting MP M4...")
matrix = MatrixPortal(status_neopixel=None)

print("Connecting to Wi-Fi...")
while True:
    try:
        matrix.network.connect()
        print("Connected to Wi-Fi!")
        break
    except Exception as e:
        print(f"Failed to connect to Wi-Fi: {e}")
        print("Retrying in 3 seconds...")
        time.sleep(3)

print("Hacking current time...")
while True:
    try:
        matrix.network.get_local_time()
        print("Time Hacked!")
        break
    except Exception as e:
        print(f"Failed to hack time: {e}")
        print("Retrying in 3 seconds...")
        time.sleep(3)

root_group = displayio.Group()

# ------------------ Clock (Left Section) ------------------
hour_label = label.Label(terminalio.FONT, text="00", color=(255, 255, 255))
minute_label = label.Label(terminalio.FONT, text="00", color=(255, 255, 255))

hour_label.x = 5
hour_label.y = HEIGHT // 4
minute_label.x = 5
minute_label.y = (HEIGHT // 4) * 3

left_group = displayio.Group()
left_group.append(hour_label)
left_group.append(minute_label)
root_group.append(left_group)

# ------------------ Divider Line ------------------
green_line_bitmap = displayio.Bitmap(DIVIDER_WIDTH, HEIGHT, 1)
green_line_palette = displayio.Palette(1)
green_line_palette[0] = (0, 255, 0)

green_line_tilegrid = displayio.TileGrid(
    green_line_bitmap,
    pixel_shader=green_line_palette,
    x=TIME_WIDTH,
    y=0
)
root_group.append(green_line_tilegrid)

# ------------------ Matrix (Right Section) ------------------
palette = create_palette()
bitmap = displayio.Bitmap(COLUMNS_WIDTH, HEIGHT, 256)
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette, x=MATRIX_X_OFFSET, y=0)

right_group = displayio.Group()
right_group.append(tile_grid)
root_group.append(right_group)

matrix.display.root_group = root_group

columns = [create_column() for _ in range(NUM_COLUMNS)]

# -----------------------------------------------------------------------------
# Main loop
# -----------------------------------------------------------------------------
while True:
    current_time = time.localtime()
    if current_time.tm_min != last_minute:
        last_minute = current_time.tm_min
        hour_label.text = f"{current_time.tm_hour:02}"
        minute_label.text = f"{current_time.tm_min:02}"

    update_columns(columns)
    draw_columns(bitmap, columns)

    if time.time() - last_sync_time >= SYNC_INTERVAL:
        while True:
            try:
                print("Hacking NTP server...")
                matrix.network.get_local_time()
                last_sync_time = time.time()
                print("Time synced!")
                break
            except AttributeError as e:
                print(f"Failed to hack time: {e}")
                print("Retrying in 1 minute...")
                time.sleep(60)

    time.sleep(UPDATE_INTERVAL)