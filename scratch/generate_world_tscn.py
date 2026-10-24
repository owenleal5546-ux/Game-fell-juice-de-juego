import os

def generate_scene_content(scene_uid):
    import sys
    sys.path.insert(0, os.path.abspath('scratch'))
    from render_preview import grid

    # Sort tiles by (y, x) for clean deterministic output
    sorted_tiles = sorted(grid.keys(), key=lambda c: (c[1], c[0]))
    
    packed_ints = []
    for cx, cy in sorted_tiles:
        ax, ay = grid[(cx, cy)]
        # Encode Godot 4 TileMap cell data:
        # int1: (cx & 0xFFFF) | ((cy & 0xFFFF) << 16)
        # int2: (source_id & 0xFFFF) | ((ax & 0xFFFF) << 16)
        # int3: (ay & 0xFFFF) | ((alt_tile & 0xFFFF) << 16)
        c_val = (cx & 0xFFFF) | ((cy & 0xFFFF) << 16)
        s_val = (0 & 0xFFFF) | ((ax & 0xFFFF) << 16)
        a_val = (ay & 0xFFFF) | ((0 & 0xFFFF) << 16)
        packed_ints.extend([c_val, s_val, a_val])
    
    tile_data_str = ", ".join(str(v) for v in packed_ints)

    content = f"""[gd_scene format=3 uid="{scene_uid}"]

[ext_resource type="PackedScene" uid="uid://cx5jsh6f7g6a0" path="res://World/parallax_background.tscn" id="1_uh6rm"]
[ext_resource type="Texture2D" uid="uid://12foa3wesyyn" path="res://World/Assets/tileset.png" id="1_wklou"]
[ext_resource type="Texture2D" uid="uid://cwpovsmkendrp" path="res://World/Assets/props/mushroom-brown.png" id="2_0etpo"]
[ext_resource type="PackedScene" uid="uid://crc2cyggi34kk" path="res://Player/player.tscn" id="2_3m2e0"]
[ext_resource type="Texture2D" uid="uid://doorv8d7wgeh2" path="res://World/Assets/props/mushroom-red.png" id="3_lpec2"]
[ext_resource type="Texture2D" uid="uid://ccierjag2o2ms" path="res://World/Assets/props/tree.png" id="4_20e5r"]
[ext_resource type="AudioStream" uid="uid://d3r51omyx66bq" path="res://Music/happywalking.ogg" id="4_gmwgb"]
[ext_resource type="PackedScene" uid="uid://8dbsyumfmwut" path="res://Enemies/Slug/Slug.tscn" id="5_o4885"]
[ext_resource type="PackedScene" uid="uid://cjcyy51wg5x2y" path="res://Enemies/Bee/bee.tscn" id="6_6l5e8"]
[ext_resource type="Texture2D" uid="uid://8jxt6ailv6ym" path="res://World/Assets/props/rock.png" id="6_f3vgq"]
[ext_resource type="PackedScene" uid="uid://dy4554uucwhh3" path="res://Enemies/PiranahPlant/piranah_plant.tscn" id="7_uqbqm"]
[ext_resource type="PackedScene" uid="uid://c566vfi6kprxp" path="res://Pickups/Carrot/carrot.tscn" id="8_8cue1"]
[ext_resource type="PackedScene" uid="uid://dh3uoh5kn40gj" path="res://Pickups/Star/star.tscn" id="9_aon80"]
[ext_resource type="Texture2D" uid="uid://diyauphhm3gtk" path="res://World/Assets/props/house.png" id="10_house"]
[ext_resource type="Texture2D" uid="uid://do0bpbirujcry" path="res://World/Assets/props/plant.png" id="11_plant"]
[ext_resource type="Texture2D" uid="uid://ksvbrrmonvec" path="res://World/Assets/props/vine.png" id="13_yxsbn"]
[ext_resource type="PackedScene" uid="uid://cgoal12345678" path="res://World/goal.tscn" id="14_goal"]
[ext_resource type="Script" uid="uid://d18pcd4rfooej" path="res://World/fall_zone.gd" id="15_fall"]

[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_4mssi"]
texture = ExtResource("1_wklou")
1:0/0 = 0
3:0/0 = 0
4:0/0 = 0
4:0/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
4:0/0/physics_layer_0/polygon_0/one_way = true
5:0/0 = 0
5:0/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
5:0/0/physics_layer_0/polygon_0/one_way = true
6:0/0 = 0
6:0/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
6:0/0/physics_layer_0/polygon_0/one_way = true
8:0/0 = 0
8:0/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
8:0/0/physics_layer_0/polygon_0/one_way = true
10:0/0 = 0
10:0/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
10:0/0/physics_layer_0/polygon_0/one_way = true
12:0/0 = 0
12:0/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
12:0/0/physics_layer_0/polygon_0/one_way = true
3:1/0 = 0
8:2/0 = 0
9:2/0 = 0
14:2/0 = 0
7:3/0 = 0
7:3/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
8:3/0 = 0
8:3/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
9:3/0 = 0
9:3/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
10:3/0 = 0
10:3/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
6:4/0 = 0
7:4/0 = 0
7:4/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
8:4/0 = 0
8:4/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
9:4/0 = 0
9:4/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
10:4/0 = 0
10:4/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
11:4/0 = 0
6:5/0 = 0
7:5/0 = 0
7:5/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
8:5/0 = 0
8:5/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
9:5/0 = 0
9:5/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
10:5/0 = 0
10:5/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
11:5/0 = 0
7:6/0 = 0
7:6/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
8:6/0 = 0
8:6/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
9:6/0 = 0
9:6/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
10:6/0 = 0
10:6/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
17:6/0 = 0
17:6/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
18:6/0 = 0
18:6/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
19:6/0 = 0
19:6/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
7:7/0 = 0
7:7/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
8:7/0 = 0
8:7/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
9:7/0 = 0
9:7/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
10:7/0 = 0
10:7/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
17:7/0 = 0
18:7/0 = 0
19:7/0 = 0
17:8/0 = 0
18:8/0 = 0
19:8/0 = 0
7:9/0 = 0
7:9/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
8:9/0 = 0
8:9/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
9:9/0 = 0
9:9/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
10:9/0 = 0
10:9/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
17:9/0 = 0
17:9/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
18:9/0 = 0
18:9/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
7:10/0 = 0
7:10/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
8:10/0 = 0
9:10/0 = 0
10:10/0 = 0
10:10/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
7:11/0 = 0
7:11/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
8:11/0 = 0
8:11/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
9:11/0 = 0
10:11/0 = 0
10:11/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)

[sub_resource type="TileSet" id="TileSet_ufbka"]
physics_layer_0/collision_layer = 1
physics_layer_0/collision_mask = 0
sources/0 = SubResource("TileSetAtlasSource_4mssi")

[sub_resource type="RectangleShape2D" id="RectangleShape2D_fallzone"]
size = Vector2(3000, 100)

[node name="World" type="Node2D" unique_id=492654115]

[node name="ParallaxBackground" parent="." unique_id=1237113930 instance=ExtResource("1_uh6rm")]

[node name="Decorations" type="Node2D" parent="." unique_id=1293677686]

[node name="House" type="Sprite2D" parent="Decorations" unique_id=554052119]
position = Vector2(110, 94)
texture = ExtResource("10_house")

[node name="Tree1" type="Sprite2D" parent="Decorations" unique_id=931386681]
position = Vector2(270, 49)
texture = ExtResource("4_20e5r")

[node name="Tree2" type="Sprite2D" parent="Decorations" unique_id=931386682]
position = Vector2(860, 113)
texture = ExtResource("4_20e5r")

[node name="Tree3" type="Sprite2D" parent="Decorations" unique_id=931386683]
position = Vector2(1800, 33)
texture = ExtResource("4_20e5r")

[node name="Rock1" type="Sprite2D" parent="Decorations" unique_id=1381225840]
position = Vector2(180, 162)
texture = ExtResource("6_f3vgq")

[node name="Rock2" type="Sprite2D" parent="Decorations" unique_id=1381225841]
position = Vector2(1150, 130)
texture = ExtResource("6_f3vgq")

[node name="Mushroom-brown1" type="Sprite2D" parent="Decorations" unique_id=554052110]
position = Vector2(210, 160)
texture = ExtResource("2_0etpo")

[node name="Mushroom-brown2" type="Sprite2D" parent="Decorations" unique_id=554052111]
position = Vector2(1715, 128)
texture = ExtResource("2_0etpo")

[node name="Mushroom-red1" type="Sprite2D" parent="Decorations" unique_id=1031390911]
position = Vector2(345, 146)
texture = ExtResource("3_lpec2")

[node name="Mushroom-red2" type="Sprite2D" parent="Decorations" unique_id=1031390912]
position = Vector2(1320, 98)
texture = ExtResource("3_lpec2")

[node name="Mushroom-red3" type="Sprite2D" parent="Decorations" unique_id=1031390913]
position = Vector2(1740, 130)
texture = ExtResource("3_lpec2")

[node name="Plant1" type="Sprite2D" parent="Decorations" unique_id=1031390914]
position = Vector2(440, 126)
texture = ExtResource("11_plant")

[node name="Plant2" type="Sprite2D" parent="Decorations" unique_id=1031390915]
position = Vector2(1520, 110)
texture = ExtResource("11_plant")

[node name="Vine1" type="Sprite2D" parent="Decorations" unique_id=346123292]
position = Vector2(750, 154)
texture = ExtResource("13_yxsbn")

[node name="Vine2" type="Sprite2D" parent="Decorations" unique_id=1740392059]
position = Vector2(835, 138)
texture = ExtResource("13_yxsbn")

[node name="Vine3" type="Sprite2D" parent="Decorations" unique_id=1740392060]
position = Vector2(945, 106)
texture = ExtResource("13_yxsbn")

[node name="Vine4" type="Sprite2D" parent="Decorations" unique_id=1740392061]
position = Vector2(1300, 138)
texture = ExtResource("13_yxsbn")

[node name="TileMap" type="TileMap" parent="." unique_id=1904224826]
tile_set = SubResource("TileSet_ufbka")
format = 2
layer_0/tile_data = PackedInt32Array({tile_data_str})

[node name="Enemies" type="Node2D" parent="." unique_id=1410174707]

[node name="Slug" parent="Enemies" unique_id=1497086131 instance=ExtResource("5_o4885")]
position = Vector2(328, 148)

[node name="PiranahPlant" parent="Enemies" unique_id=1797481271 instance=ExtResource("7_uqbqm")]
position = Vector2(680, 112)

[node name="Bee" parent="Enemies" unique_id=789989086 instance=ExtResource("6_6l5e8")]
position = Vector2(840, 70)

[node name="Slug2" parent="Enemies" unique_id=1995565182 instance=ExtResource("5_o4885")]
position = Vector2(1024, 116)

[node name="Bee2" parent="Enemies" unique_id=1037837107 instance=ExtResource("6_6l5e8")]
position = Vector2(1272, 90)

[node name="PiranahPlant2" parent="Enemies" unique_id=973720923 instance=ExtResource("7_uqbqm")]
position = Vector2(1360, 96)

[node name="Slug3" parent="Enemies" unique_id=1111111111 instance=ExtResource("5_o4885")]
position = Vector2(1584, 100)

[node name="Pickups" type="Node2D" parent="." unique_id=186648387]

[node name="Carrot1" parent="Pickups" unique_id=1173454715 instance=ExtResource("8_8cue1")]
position = Vector2(208, 145)

[node name="Carrot2" parent="Pickups" unique_id=51288067 instance=ExtResource("8_8cue1")]
position = Vector2(232, 130)

[node name="Carrot3" parent="Pickups" unique_id=370041027 instance=ExtResource("8_8cue1")]
position = Vector2(256, 145)

[node name="Carrot4" parent="Pickups" unique_id=499487656 instance=ExtResource("8_8cue1")]
position = Vector2(512, 120)

[node name="Carrot5" parent="Pickups" unique_id=850262994 instance=ExtResource("8_8cue1")]
position = Vector2(528, 105)

[node name="Carrot6" parent="Pickups" unique_id=166289352 instance=ExtResource("8_8cue1")]
position = Vector2(544, 120)

[node name="Carrot7" parent="Pickups" unique_id=1111111114 instance=ExtResource("8_8cue1")]
position = Vector2(656, 85)

[node name="Carrot8" parent="Pickups" unique_id=1111111115 instance=ExtResource("8_8cue1")]
position = Vector2(680, 70)

[node name="Carrot9" parent="Pickups" unique_id=1111111116 instance=ExtResource("8_8cue1")]
position = Vector2(704, 85)

[node name="Carrot10" parent="Pickups" unique_id=1111111117 instance=ExtResource("8_8cue1")]
position = Vector2(824, 75)

[node name="Carrot11" parent="Pickups" unique_id=1111111118 instance=ExtResource("8_8cue1")]
position = Vector2(840, 55)

[node name="Carrot12" parent="Pickups" unique_id=1111111119 instance=ExtResource("8_8cue1")]
position = Vector2(856, 75)

[node name="Carrot13" parent="Pickups" unique_id=1111111120 instance=ExtResource("8_8cue1")]
position = Vector2(1176, 115)

[node name="Carrot14" parent="Pickups" unique_id=1111111121 instance=ExtResource("8_8cue1")]
position = Vector2(1192, 100)

[node name="Carrot15" parent="Pickups" unique_id=1111111122 instance=ExtResource("8_8cue1")]
position = Vector2(1208, 115)

[node name="Carrot16" parent="Pickups" unique_id=1111111123 instance=ExtResource("8_8cue1")]
position = Vector2(1648, 105)

[node name="Carrot17" parent="Pickups" unique_id=1111111124 instance=ExtResource("8_8cue1")]
position = Vector2(1672, 90)

[node name="Carrot18" parent="Pickups" unique_id=1111111125 instance=ExtResource("8_8cue1")]
position = Vector2(1696, 105)

[node name="Star1" parent="Pickups" unique_id=1856101220 instance=ExtResource("9_aon80")]
position = Vector2(936, 55)

[node name="Star2" parent="Pickups" unique_id=1856101221 instance=ExtResource("9_aon80")]
position = Vector2(1328, 65)

[node name="Player" parent="." unique_id=1128907737 instance=ExtResource("2_3m2e0")]
position = Vector2(40, 155)

[node name="Goal" parent="." unique_id=1111111126 instance=ExtResource("14_goal")]
position = Vector2(1750, 120)

[node name="AudioStreamPlayer" type="AudioStreamPlayer" parent="." unique_id=1842792974]
stream = ExtResource("4_gmwgb")
autoplay = true

[node name="FallZone" type="Area2D" parent="." unique_id=999888777]
position = Vector2(950, 400)
collision_layer = 0
collision_mask = 2
script = ExtResource("15_fall")

[node name="CollisionShape2D" type="CollisionShape2D" parent="FallZone" unique_id=1602885149]
shape = SubResource("RectangleShape2D_fallzone")
"""
    return content

if __name__ == '__main__':
    # Write Scenes/World.tscn (UID: uid://du1bilx8oos0i)
    c1 = generate_scene_content("uid://du1bilx8oos0i")
    with open('Scenes/World.tscn', 'w', encoding='utf-8') as f:
        f.write(c1)
    print("Written Scenes/World.tscn")

    # Write World/world.tscn (UID: uid://bllxgiuvjqf3u)
    c2 = generate_scene_content("uid://bllxgiuvjqf3u")
    with open('World/world.tscn', 'w', encoding='utf-8') as f:
        f.write(c2)
    print("Written World/world.tscn")
