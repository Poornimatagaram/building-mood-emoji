"""One big circular emoji at a time, centered on the building, styled like
a classic pixel-art emoji sheet (solid black ring outline, flat yellow fill).
A deliberate wave at the camera swaps to a new random emoji.
Press 'q' in the camera window to quit."""
import sys, time, random
import cv2
from gbsim import WebDisplay, Color

name = sys.argv[1]
base = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8787/api"
d = WebDisplay(name, base)
f = d.makeframe()
ROWS, COLS = f.nrows(), f.ncols()  # 17, 9

def safe_color(r, g, b):
    return Color(max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))))

# ---------- Palette ----------
BG     = safe_color(6, 6, 6)
BORDER = safe_color(10, 8, 5)        # push darker so it survives bloom
FACE   = safe_color(220, 175, 30)    # slightly less intense than before
K      = safe_color(15, 11, 8)
W      = safe_color(210, 205, 195)
T      = safe_color(85, 130, 195)
R      = safe_color(180, 55, 50)
H      = safe_color(200, 65, 90)
S      = safe_color(225, 185, 50)

PALETTE = {
    ".": None,
    "O": BORDER, "F": FACE,
    "K": K, "W": W, "T": T, "R": R, "H": H, "S": S,
}

CIRCLE = [
    "...OOO...",
    ".OFFFFFO.",
    "OFFFFFFFO",
    "OFFFFFFFO",
    "OFFFFFFFO",
    "OFFFFFFFO",
    "OFFFFFFFO",
    "OFFFFFFFO",
    "OFFFFFFFO",
    ".OFFFFFO.",
    "...OOO...",
]

def with_overrides(overrides):
    grid = [list(row) for row in CIRCLE]
    for (r, c), ch in overrides.items():
        grid[r][c] = ch
    return ["".join(row) for row in grid]

EMOJIS = {
    "smile 🙂": with_overrides({
        (3, 2): "K", (3, 6): "K",
        (7, 3): "K", (7, 4): "K", (7, 5): "K",
        (6, 2): "K", (6, 6): "K",
    }),
    "cool 😎": with_overrides({
        (3, 1): "K", (3, 2): "K", (3, 3): "K", (3, 4): "K",
        (3, 5): "K", (3, 6): "K", (3, 7): "K",
        (7, 3): "K", (7, 4): "K", (7, 5): "K",
    }),
    "nerd 🤓": with_overrides({
        (2, 1): "K", (2, 2): "K", (2, 3): "K",
        (2, 5): "K", (2, 6): "K", (2, 7): "K",
        (3, 2): "W", (3, 6): "W",
        (4, 2): "K", (4, 6): "K",
        (7, 3): "W", (7, 4): "W", (7, 5): "W",
    }),
    "laugh 😂": with_overrides({
        (3, 2): "K", (3, 6): "K",
        (4, 2): "T", (4, 6): "T",
        (7, 2): "W", (7, 3): "W", (7, 4): "W", (7, 5): "W", (7, 6): "W",
        (8, 3): "K", (8, 4): "K", (8, 5): "K",
    }),
    "wink 😉": with_overrides({
        (3, 2): "K",
        (3, 5): "K", (3, 6): "K",
        (7, 3): "K", (7, 4): "K", (7, 5): "K",
        (6, 2): "K", (6, 6): "K",
    }),
    "heart-eyes 😍": with_overrides({
        (2, 1): "H", (2, 2): "H", (3, 1): "H", (3, 2): "H",
        (2, 5): "H", (2, 6): "H", (3, 5): "H", (3, 6): "H",
        (7, 3): "K", (7, 4): "K", (7, 5): "K",
    }),
    "star-struck 🤩": with_overrides({
        (2, 2): "S", (3, 1): "S", (3, 2): "S", (3, 3): "S", (4, 2): "S",
        (2, 6): "S", (3, 5): "S", (3, 6): "S", (3, 7): "S", (4, 6): "S",
        (7, 3): "W", (7, 4): "W", (7, 5): "W",
        (8, 4): "K",
    }),
}

EMOJI_H = 11
START_ROW = (ROWS - EMOJI_H) // 2  # vertically centered, margin top & bottom

def draw_emoji(frame, pattern):
    for r in range(ROWS):
        for c in range(COLS):
            frame[r][c] = BG
    for i, row in enumerate(pattern):
        for c, ch in enumerate(row):
            color = PALETTE.get(ch)
            if color is not None:
                frame[START_ROW + i][c] = color

def soft_blink(display, frame_obj):
    """A brief dim-out instead of a harsh white flash."""
    for r in range(ROWS):
        for c in range(COLS):
            frame_obj[r][c] = BG
    display.send(frame_obj)
    time.sleep(0.15)

# ---------- Camera + trigger loop ----------
cap = cv2.VideoCapture(0)
back_sub = cv2.createBackgroundSubtractorMOG2(history=50, varThreshold=40)

current_name = random.choice(list(EMOJIS.keys()))
draw_emoji(f, EMOJIS[current_name])
d.send(f)
print(f"Showing: {current_name}")

last_trigger = 0
COOLDOWN = 6.0     # only a real deliberate wave should trigger a change
MIN_AREA = 12000   # ignores small head/body shifts

print("Do one clear, deliberate wave close to the camera to get a new emoji. Press 'q' to quit.")

while True:
    ok, frame = cap.read()
    if not ok:
        break
    frame = cv2.flip(frame, 1)

    mask = back_sub.apply(frame)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    now = time.time()
    if contours and now - last_trigger > COOLDOWN:
        biggest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(biggest) > MIN_AREA:
            x, y, w, h = cv2.boundingRect(biggest)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            choices = [n for n in EMOJIS if n != current_name]
            current_name = random.choice(choices)
            soft_blink(d, f)
            draw_emoji(f, EMOJIS[current_name])
            d.send(f)
            print(f"Showing: {current_name}")
            last_trigger = now

    cv2.imshow("Motion (press q to quit)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()