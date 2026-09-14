"""Draw a checkerboard snakes & ladders board with visible connecting trails."""
import sys, time
from gbsim import WebDisplay, Color

name = sys.argv[1]
base = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8787/api"
d = WebDisplay(name, base)
f = d.makeframe()
ROWS, COLS = f.nrows(), f.ncols()
TOTAL_SQUARES = ROWS * COLS

def safe_color(r, g, b):
    return Color(max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))))

LADDERS = {5: 28, 15: 44, 35: 52, 51: 74, 68: 90, 83: 105, 98: 120, 112: 135}
SNAKES  = {30: 10, 48: 22, 65: 38, 79: 55, 94: 60, 108: 72, 125: 82, 140: 100}

CREAM  = safe_color(150, 120, 80)   # warm sand
TAN    = safe_color(110, 85, 55)    # warm brown
LADDER_A = safe_color(30, 120, 55)  # forest green
LADDER_B = safe_color(60, 160, 80)  # slightly lighter green
SNAKE_A  = safe_color(140, 25, 25)  # deep red
SNAKE_B  = safe_color(180, 60, 45)  # lighter red

def square_to_rc(n):
    idx = n - 1
    row_from_bottom = idx // COLS
    row = ROWS - 1 - row_from_bottom
    pos = idx % COLS
    col = pos if row_from_bottom % 2 == 0 else (COLS - 1 - pos)
    return row, col

def line_cells(r0, c0, r1, c1):
    """Bresenham's line, so a ladder/snake draws as a connected trail."""
    points = []
    dr, dc = abs(r1 - r0), abs(c1 - c0)
    sr = 1 if r0 < r1 else -1
    sc = 1 if c0 < c1 else -1
    err = dr - dc
    r, c = r0, c0
    while True:
        points.append((r, c))
        if r == r1 and c == c1:
            break
        e2 = 2 * err
        if e2 > -dc:
            err -= dc
            r += sr
        if e2 < dr:
            err += dr
            c += sc
    return points

# checkerboard background
for row_from_bottom in range(ROWS):
    row = ROWS - 1 - row_from_bottom
    for pos in range(COLS):
        col = pos if row_from_bottom % 2 == 0 else (COLS - 1 - pos)
        f[row][col] = CREAM if (row + col) % 2 == 0 else TAN

# ladders: green trail from bottom to top
for start, end in LADDERS.items():
    r0, c0 = square_to_rc(start)
    r1, c1 = square_to_rc(end)
    for i, (r, c) in enumerate(line_cells(r0, c0, r1, c1)):
        f[r][c] = LADDER_A if i % 2 == 0 else LADDER_B

# snakes: red trail from head to tail
for start, end in SNAKES.items():
    r0, c0 = square_to_rc(start)
    r1, c1 = square_to_rc(end)
    for i, (r, c) in enumerate(line_cells(r0, c0, r1, c1)):
        f[r][c] = SNAKE_A if i % 2 == 0 else SNAKE_B

# start (bottom-left) and finish (top) markers
r, c = square_to_rc(1)
f[r][c] = safe_color(255, 255, 255)
r, c = square_to_rc(TOTAL_SQUARES)
f[r][c] = safe_color(255, 215, 0)

d.send(f)
print(f"Board drawn. {TOTAL_SQUARES} squares, {len(LADDERS)} ladders, {len(SNAKES)} snakes.")
while True:
    time.sleep(1)