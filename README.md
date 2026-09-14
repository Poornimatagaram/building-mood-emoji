# The Building Notices You

Wave at a webcam and MIT's Green Building lights up a giant pixel-art emoji, live.

Built for Sundai Hack 140 — Beyond Tetris: Building-Scale Physical AI for the MIT Green Building.

## What it does

A webcam watches for a deliberate wave using OpenCV background subtraction.
When it detects one, the building's 17x9 window grid lights up a large,
clean pixel-art emoji -- smiling, cool, laughing, winking, star-struck, and
more -- centered across the whole facade. Each wave swaps to a new random
emoji.

## Run it

```bash
pip install -r requirements.txt
python3 mood_emoji.py <your-instance-name> https://sundai.willsarg.com/api
```

`board.py` is an earlier prototype (a snakes-and-ladders board on the
building) kept here to show the project's iteration.
