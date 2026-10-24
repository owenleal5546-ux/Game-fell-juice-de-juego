import re
from PIL import Image, ImageDraw
import numpy as np

tileset = Image.open('World/Assets/tileset.png').convert('RGBA')

# Tile grid mapping: (x, y) -> (atlas_x, atlas_y)
grid = {}

def add_terrain(x1, x2, y1, y2=14):
    """Adds a grounded terrain mass from x1 to x2 (inclusive) and y1 to y2."""
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
                    grid[(x, y)] = (7, 6) # Bot-left
                elif x == x2:
                    grid[(x, y)] = (10, 6) # Bot-right
                else:
                    grid[(x, y)] = (8, 6) if x % 2 == 0 else (9, 6) # Bot-mid
            else:
                if x == x1:
                    grid[(x, y)] = (7, 4) if y % 2 == 0 else (7, 5) # Mid-left
                elif x == x2:
                    grid[(x, y)] = (10, 4) if y % 2 == 0 else (10, 5) # Mid-right
                else:
                    grid[(x, y)] = (8, 4) if (x + y) % 2 == 0 else (9, 4) # Dirt center

def add_wood_bridge(x1, x2, y, support_ground_y=None, support_xs=None):
    """Adds a one-way wooden bridge from x1 to x2 at height y, with anchored support pillars."""
    for x in range(x1, x2 + 1):
        if x == x1:
            grid[(x, y)] = (4, 0)
        elif x == x2:
            grid[(x, y)] = (6, 0)
        else:
            grid[(x, y)] = (5, 0)
    
    # Add vertical support pillars down to ground
    if support_ground_y is not None:
        if support_xs is None:
            support_xs = [x1, x2]
        for sx in support_xs:
            for sy in range(y + 1, support_ground_y):
                if (sx, sy) not in grid:
                    grid[(sx, sy)] = (3, 1) # Non-colliding wood support pole

def add_stone_pillar(x1, x2, y1, y2=14):
    """Adds a stone ruin platform supported by stone columns down to bedrock."""
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

# Left invisible/solid wall border at x = -1
for y in range(0, 15):
    grid[(-1, y)] = (10, 6)

# ==============================================================================
# 1. ZONE 1: Inicio Seguro y Pradera Inicial (x = 0..22)
# ==============================================================================
# Ground meadow at y = 11 down to 14
add_terrain(0, 15, 11, 14)

# Slight gentle step up at x = 16..22 (height y = 10, exactly 1 tile up!)
add_terrain(16, 22, 10, 14)

# ==============================================================================
# 2. ZONE 2: Valle del Arroyo y Plataformas Soportadas (x = 23..45)
# ==============================================================================
# Riverbed ground at y = 13 (with safe riverbed floor at y=13..14)
add_terrain(23, 45, 13, 14)

# Stepping hill 1: x = 25..28, y = 9 (height diff from x=22 is 1 tile: 10 -> 9; gap is 2 tiles: 22 to 25)
add_terrain(25, 28, 9, 14)

# Wooden suspension bridge: x = 31..35, y = 9 (gap from x=28 is 2 tiles: 28 to 31; height diff = 0)
add_wood_bridge(31, 35, 9, support_ground_y=13, support_xs=[31, 33, 35])

# Sturdy Cliff Mound: x = 38..44, y = 8 (gap from x=35 is 2 tiles: 35 to 38; height diff = 1 tile: 9 -> 8)
add_terrain(38, 44, 8, 14)

# ==============================================================================
# 3. ZONE 3: El Gran Roble y Plataformas Elevadas (x = 45..68)
# ==============================================================================
# Forest floor baseline at y = 14
add_terrain(45, 67, 14, 14)

# Platform 1 (Canopy walkway): x = 47..51, y = 8 (gap from x=44 is 2 tiles: 44 to 47; height diff = 0)
add_stone_pillar(47, 51, 8, 14)

# Platform 2 (Canopy center): x = 54..58, y = 7 (gap from x=51 is 2 tiles: 51 to 54; height diff = 1 tile: 8 -> 7)
add_stone_pillar(54, 58, 7, 14)

# Upper Secret Branch (for Star 1 reward): x = 57..60, y = 5 (step up 2 tiles from y=7, overlapping!)
add_wood_bridge(57, 60, 5, support_ground_y=7, support_xs=[57, 60])

# Platform 3 (Canopy descent): x = 61..65, y = 8 (gap from x=58 is 2 tiles: 58 to 61; height diff = 1 tile down: 7 -> 8)
add_terrain(61, 65, 8, 14)

# ==============================================================================
# 4. ZONE 4: Ruinas Antiguas del Bosque y Desfiladero (x = 66..91)
# ==============================================================================
# Platform 1 (Ancient Ruin Terrace): x = 68..72, y = 9 (gap from x=65 is 2 tiles: 65 to 68; height diff = 1 tile down: 8 -> 9)
add_stone_pillar(68, 72, 9, 14)

# Platform 2 (Sunken Pillar): x = 75..78, y = 9 (gap from x=72 is 2 tiles: 72 to 75; height diff = 0: 9 -> 9)
add_stone_pillar(75, 78, 9, 14)

# Platform 3 (Elevated Ruin Arch): x = 81..86, y = 7 (gap from x=78 is 2 tiles: 78 to 81; height diff = 2 tiles up: 9 -> 7)
add_stone_pillar(81, 86, 7, 14)

# ==============================================================================
# 5. ZONE 5: Mesetas Finales y Meta Triunfal (x = 88..115)
# ==============================================================================
# Terrace 1: x = 89..93, y = 8 (gap from x=86 is 2 tiles: 86 to 89; height diff = 1 tile down: 7 -> 8)
add_terrain(89, 93, 8, 14)

# Terrace 2: x = 96..100, y = 7 (gap from x=93 is 2 tiles: 93 to 96; height diff = 1 tile up: 8 -> 7)
add_terrain(96, 100, 7, 14)

# Wooden connection bridge: x = 102..105, y = 8 (gap from x=100 is 1 tile: 100 to 102; height diff = 1 tile down: 7 -> 8)
add_wood_bridge(102, 105, 8, support_ground_y=14, support_xs=[102, 105])

# Grand Victory Plateau: x = 106..115, y = 9 (connected directly!)
add_terrain(106, 115, 9, 14)

# Right border wall at x = 116
for y in range(0, 15):
    grid[(116, y)] = (10, 6)

print(f'Total tiles generated: {len(grid)}')

# Check every platform top and calculate jump distances
# Platforms list: (name, x1, x2, y)
platforms = [
    ("Inicio Meadow", 0, 15, 11),
    ("Inicio Plateau", 16, 22, 10),
    ("Stepping Hill", 25, 28, 9),
    ("Wood Bridge 1", 31, 35, 9),
    ("Cliff Mound", 38, 44, 8),
    ("Canopy Walk 1", 47, 51, 8),
    ("Canopy Center", 54, 58, 7),
    ("Upper Secret Branch", 57, 60, 5),
    ("Canopy Descent", 61, 65, 8),
    ("Ruin Terrace 1", 68, 72, 9),
    ("Sunken Pillar", 75, 78, 9),
    ("Ruin Arch", 81, 86, 7),
    ("Final Terrace 1", 89, 93, 8),
    ("Final Terrace 2", 96, 100, 7),
    ("Wood Bridge 2", 102, 105, 8),
    ("Victory Plateau", 106, 115, 9),
]

print("\n--- VALIDACIÓN DE REGLAS DE SALTO Y ACCESIBILIDAD ---")
all_valid = True
for i in range(len(platforms) - 1):
    p1 = platforms[i]
    p2 = platforms[i+1]
    # If skipping upper branch for main path, also check p1 to p3
    h_gap = max(0, p2[1] - p1[2] - 1)
    v_diff = p1[3] - p2[3] # positive means p2 is higher than p1
    print(f"{p1[0]} (x={p1[2]}, y={p1[3]}) -> {p2[0]} (x={p2[1]}, y={p2[3]}): H-Gap={h_gap} blocks, V-Up={v_diff} blocks", end="")
    
    if h_gap > 4:
        print(" -> ERROR: Salto horizontal > 4 bloques!")
        all_valid = False
    elif v_diff > 3:
        print(" -> ERROR: Altura vertical > 3 bloques!")
        all_valid = False
    else:
        print(" -> OK (Cumple reglas)")

if all_valid:
    print("\n>>> ¡TODOS LOS SALTOS CUMPLEN ESTRICTAMENTE LAS REGLAS DE ACCESIBILIDAD! <<<\n")
