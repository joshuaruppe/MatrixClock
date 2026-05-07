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
SYNC_RETRY_INTERVAL = 60

USE_24_HOUR = False

last_minute = None
next_sync_attempt = time.time() + SYNC_INTERVAL

# =============================================================================
# Helper Functions
# =============================================================================

def retry_forever(action, label, delay=3):
    while True:
        try:
            action()
            print(f"{label}: ok")
            return
        except Exception as e:
            print(f"{label} failed: {e}; retrying in {delay}s")
            time.sleep(delay)

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
    bitmap.fill(0)
    for col_index, column in enumerate(columns):
        for trail_index, char in enumerate(column["trail"]):
            if char == " ":
                continue
            y = column["y"] - trail_index
            if 0 <= y < COLUMN_HEIGHT:
                if trail_index == 0:
                    bitmap[col_index, y] = random.randint(240, 255)
                else:
                    bitmap[col_index, y] = random.randint(100, 200)

# =============================================================================
# Main Program
# =============================================================================

print("Starting MP M4...")
matrix = MatrixPortal(status_neopixel=None)

retry_forever(matrix.network.connect, "Wi-Fi connect")
retry_forever(matrix.network.get_local_time, "Time sync")

root_group = displayio.Group()

# ------------------ Clock (Left Section) ------------------
hour_label = label.Label(terminalio.FONT, text="00", color=(255, 255, 255))
minute_label = label.Label(terminalio.FONT, text="00", color=(255, 255, 255))

hour_label.x = 5
hour_label.y = HEIGHT // 4
minute_label.x = 5
minute_label.y = (HEIGHT // 4) * 3

pm_dot_bitmap = displayio.Bitmap(1, 1, 1)
pm_dot_palette = displayio.Palette(1)
pm_dot_palette[0] = (255, 255, 255)
pm_dot = displayio.TileGrid(pm_dot_bitmap, pixel_shader=pm_dot_palette, x=TIME_WIDTH - 2, y=0)
pm_dot.hidden = True

left_group = displayio.Group()
left_group.append(hour_label)
left_group.append(minute_label)
left_group.append(pm_dot)
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
        hour = current_time.tm_hour
        if USE_24_HOUR:
            pm_dot.hidden = True
        else:
            pm_dot.hidden = hour < 12
            hour = (hour - 1) % 12 + 1
        hour_label.text = f"{hour:02}"
        minute_label.text = f"{current_time.tm_min:02}"

    update_columns(columns)
    draw_columns(bitmap, columns)

    if time.time() >= next_sync_attempt:
        try:
            print("Hacking NTP server...")
            matrix.network.get_local_time()
            last_sync_time = time.time()
            next_sync_attempt = last_sync_time + SYNC_INTERVAL
            print("Time synced!")
        except Exception as e:
            print(f"Failed to hack time: {e}")
            print("Retrying in 1 minute...")
            next_sync_attempt = time.time() + SYNC_RETRY_INTERVAL

    time.sleep(UPDATE_INTERVAL)