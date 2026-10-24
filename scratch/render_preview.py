import re
from PIL import Image, ImageDraw
import numpy as np

tileset = Image.open('World/Assets/tileset.png').convert('RGBA')

grid = {}

def add_terrain(x1, x2, y1, y2=14):
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            if y == y1:
                if x == x1:
                    grid[(x, y)] = (7, 3) # Top-left
                elif x == x2:
                    grid[(x, y)] = (10, 3) # Top-right
                else:
                    grid[(x, y)] = (8, 3) if x % 2 == 0 else (9, 3) # Top-mid
            elif y == y2:
                if x == x1:
                    grid[(x, y)] = (7, 7) # Bot-left
                elif x == x2:
                    grid[(x, y)] = (10, 7) # Bot-right
                else:
                    grid[(x, y)] = (8, 7) if x % 2 == 0 else (9, 7) # Bot-mid
            else:
                if x == x1:
                    grid[(x, y)] = (7, 4) if y % 2 == 0 else (7, 5) # Mid-left
                elif x == x2:
                    grid[(x, y)] = (10, 4) if y % 2 == 0 else (10, 5) # Mid-right
                else:
                    grid[(x, y)] = (8, 4) if (x + y) % 2 == 0 else (9, 4) # Dirt center

def add_wood_bridge(x1, x2, y, support_ground_y=None, support_xs=None):
    for x in range(x1, x2 + 1):
        if x == x1:
            grid[(x, y)] = (4, 0)
        elif x == x2:
            grid[(x, y)] = (6, 0)
        else:
            grid[(x, y)] = (5, 0)
    
    if support_ground_y is not None:
        if support_xs is None:
            support_xs = [x1, x2]
        for sx in support_xs:
            for sy in range(y + 1, support_ground_y):
                if (sx, sy) not in grid:
                    grid[(sx, sy)] = (3, 1)

def add_stone_pillar(x1, x2, y1, y2=14):
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            if y == y1:
                if x == x1:
                    grid[(x, y)] = (17, 6) # Left stone top
                elif x == x2:
                    grid[(x, y)] = (19, 6) # Right stone top
                else:
                    grid[(x, y)] = (18, 6) # Mid stone top
            else:
                if x == x1:
                    grid[(x, y)] = (17, 7) if y % 2 == 0 else (17, 8)
                elif x == x2:
                    grid[(x, y)] = (19, 7) if y % 2 == 0 else (19, 8)
                else:
                    grid[(x, y)] = (18, 7) if y % 2 == 0 else (18, 8)

# Left boundary wall
for y in range(0, 15):
    grid[(-1, y)] = (10, 6)

# 1. ZONE 1
add_terrain(0, 15, 11, 14)
add_terrain(16, 22, 10, 14)

# 2. ZONE 2
add_terrain(23, 45, 13, 14)
add_terrain(25, 28, 9, 14)
add_wood_bridge(31, 35, 9, support_ground_y=13, support_xs=[31, 33, 35])
add_terrain(38, 44, 8, 14)

# 3. ZONE 3
add_terrain(45, 67, 14, 14)
add_stone_pillar(47, 51, 8, 14)
add_stone_pillar(54, 58, 7, 14)
add_wood_bridge(57, 60, 5, support_ground_y=7, support_xs=[57, 60])
add_terrain(61, 65, 8, 14)

# 4. ZONE 4
add_stone_pillar(68, 72, 9, 14)
add_stone_pillar(75, 78, 9, 14)
add_stone_pillar(81, 86, 7, 14)

# 5. ZONE 5
add_terrain(89, 93, 8, 14)
add_terrain(96, 100, 7, 14)
add_wood_bridge(102, 105, 8, support_ground_y=14, support_xs=[102, 105])
add_terrain(106, 115, 9, 14)

# Right boundary wall
for y in range(0, 15):
    grid[(116, y)] = (10, 6)

W = 118 * 16
H = 15 * 16
canvas = Image.new('RGBA', (W, H), (45, 42, 65, 255))

bg = Image.open('World/Assets/background.png').convert('RGBA')
mg = Image.open('World/Assets/middleground.png').convert('RGBA')
for bx in range(0, W, bg.width):
    canvas.alpha_composite(bg, (bx, 0))
    canvas.alpha_composite(mg, (bx, 0))

def draw_prop(name, px, py):
    p = Image.open(f'World/Assets/props/{name}.png').convert('RGBA')
    canvas.alpha_composite(p, (int(px - p.width // 2), int(py - p.height // 2)))

# Props with corrected heights
draw_prop('house', 110, 94)
draw_prop('tree', 270, 49)
draw_prop('rock', 180, 162)
draw_prop('mushroom-brown', 210, 160)
draw_prop('mushroom-red', 345, 146)
draw_prop('plant', 440, 126)
draw_prop('tree', 860, 113)
draw_prop('vine', 750, 154)
draw_prop('vine', 835, 138)
draw_prop('vine', 945, 106)
draw_prop('rock', 1150, 130)
draw_prop('mushroom-red', 1320, 98)
draw_prop('vine', 1300, 138)
draw_prop('plant', 1520, 110)
draw_prop('tree', 1800, 33)
draw_prop('mushroom-brown', 1715, 128)
draw_prop('mushroom-red', 1740, 130)

# Draw tiles
for (cx, cy), (ax, ay) in grid.items():
    if cx < 0 or cx >= 118 or cy < 0 or cy >= 15:
        continue
    tile = tileset.crop((ax * 16, ay * 16, (ax + 1) * 16, (ay + 1) * 16))
    canvas.alpha_composite(tile, (cx * 16, cy * 16))

# Annotations
draw = ImageDraw.Draw(canvas)
draw.rectangle([40 - 7, 155 - 10, 40 + 7, 155 + 10], fill=(0, 255, 255, 200), outline=(255, 255, 255))
draw.text((40 - 15, 130), "Player", fill=(255, 255, 255))

draw.rectangle([1760 - 10, 128 - 15, 1760 + 10, 128 + 15], fill=(255, 215, 0, 220), outline=(255, 255, 255))
draw.text((1760 - 15, 95), "GOAL", fill=(255, 215, 0))

enemies = [
    ("Slug 1", 328, 148),
    ("Piranah 1", 680, 112),
    ("Bee 1", 840, 70),
    ("Slug 2", 1024, 116),
    ("Bee 2", 1272, 90),
    ("Piranah 2", 1360, 96),
    ("Slug 3", 1584, 100)
]
for name, ex, ey in enemies:
    draw.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=(255, 50, 50, 220), outline=(255, 255, 255))
    draw.text((ex - 12, ey - 18), name, fill=(255, 100, 100))

carrots = [
    (208, 145), (232, 130), (256, 145),
    (512, 120), (528, 105), (544, 120),
    (656, 85), (680, 70), (704, 85),
    (824, 75), (840, 55), (856, 75),
    (1176, 115), (1192, 100), (1208, 115),
    (1648, 105), (1672, 90), (1696, 105)
]
for cx, cy in carrots:
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 165, 0, 220))

stars = [(936, 55), (1328, 65)]
for sx, sy in stars:
    draw.polygon([(sx, sy - 7), (sx + 5, sy + 6), (sx - 6, sy - 2), (sx + 6, sy - 2), (sx - 5, sy + 6)], fill=(255, 255, 0))

canvas.save('scratch/preview_new_world.png')
print('Preview image saved to scratch/preview_new_world.png')
