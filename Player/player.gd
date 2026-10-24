extends CharacterBody2D

const BloodSplatterScene = preload("res://VFX/blood_splatter.tscn")
const PickupParticleScene = preload("res://VFX/pickup_particle.tscn")
const HurtboxClass = preload("res://Combat/hurtbox.gd")

const SPEED = 110.0
const JUMP_VELOCITY = -200.0

@export var max_health: int = 3
var current_health: int = 3
var is_invulnerable: bool = false
var is_hurt: bool = false
var is_dead: bool = false

var _invulnerable_timer: float = 0.0
var _hurt_timer: float = 0.0
var _attack_timer: float = 0.0
var facing_direction: int = 1

var gravity = 300

## Game Feel & Jugabilidad (Coyote Time & Input Buffering)
@export_group("Game Feel")
@export var coyote_time: float = 0.14
@export var jump_buffer_time: float = 0.14

var _coyote_timer: float = 0.0
var _jump_buffer_timer: float = 0.0
var _was_on_floor: bool = false
var _previous_velocity_y: float = 0.0

## Efectos de Sonido Procedurales Retro
var _sfx_player: AudioStreamPlayer = null
var _sfx_jump: AudioStreamWAV = null
var _sfx_pickup: AudioStreamWAV = null
var _sfx_hurt: AudioStreamWAV = null
var _sfx_land: AudioStreamWAV = null

## Registro periódico de coordenadas (x, y) durante la partida
@export var position_sample_interval: float = 0.5
var _sample_timer: float = 0.0
var position_history: Array[Dictionary] = []

@onready var animated_sprite_2d = $AnimatedSprite2D
@onready var hurtbox = $Hurtbox
@onready var stomp_detector = $StompDetector
@onready var attack_hitbox = $AttackHitbox
@onready var hud = $PlayerHUD
@onready var camera_2d = $Camera2D

func _ready() -> void:
	current_health = max_health
	position_history.clear()
	_sample_timer = 0.0
	record_current_position()
	_setup_sfx()
	if hud:
		hud.setup(max_health, current_health)
	if hurtbox:
		hurtbox.hit_received.connect(_on_hit_received)
	if attack_hitbox:
		attack_hitbox.monitoring = false
		attack_hitbox.monitorable = false
	if camera_2d:
		camera_2d.position = Vector2.ZERO
		camera_2d.offset = Vector2.ZERO
		camera_2d.zoom = Vector2(1, 1)
		camera_2d.limit_left = 0
		camera_2d.limit_top = 0
		camera_2d.limit_bottom = 240
		camera_2d.position_smoothing_enabled = true
		camera_2d.position_smoothing_speed = 6.0
		camera_2d.drag_horizontal_enabled = false
		camera_2d.drag_vertical_enabled = false
		camera_2d.drag_left_margin = 0.0
		camera_2d.drag_right_margin = 0.0
		camera_2d.drag_top_margin = 0.0
		camera_2d.drag_bottom_margin = 0.0
		_setup_camera_limits()

func _setup_camera_limits() -> void:
	if not camera_2d:
		return
	if not is_inside_tree() or not get_tree() or not get_tree().current_scene:
		return
	var tilemap = get_tree().current_scene.find_child("TileMap", true, false)
	if tilemap and tilemap is TileMap:
		var map_rect = tilemap.get_used_rect()
		var tile_size = tilemap.tile_set.tile_size
		var left_px = map_rect.position.x * tile_size.x
		var right_px = map_rect.end.x * tile_size.x
		var bottom_px = map_rect.end.y * tile_size.y
		
		var half_screen_w = (get_viewport_rect().size.x / camera_2d.zoom.x) / 2.0
		camera_2d.limit_left = max(0, int(left_px))
		camera_2d.limit_top = 0
		camera_2d.limit_bottom = max(240, int(bottom_px))
		camera_2d.limit_right = int(right_px + half_screen_w)

## Método reutilizable para vibración de cámara
func apply_screenshake(intensity: float = 4.0, duration: float = 0.2) -> void:
	if camera_2d and camera_2d.has_method("apply_screenshake"):
		camera_2d.apply_screenshake(intensity, duration)

func _physics_process(delta: float) -> void:
	_update_timers(delta)
	if not is_dead:
		_update_position_tracking(delta)

	if is_dead:
		velocity.y += gravity * delta
		move_and_slide()
		return

	if global_position.y > 320 and not is_dead:
		die()
		return

	if is_hurt:
		velocity.y += gravity * delta
		if animated_sprite_2d:
			animated_sprite_2d.play("hurt")
		move_and_slide()
		return

	if not is_on_floor():
		velocity.y += gravity * delta

	# Handle Stomp on enemies while falling
	if velocity.y > 0:
		_check_stomp_enemies()

	# Coyote Time: permite saltar unos instantes después de dejar una repisa
	if is_on_floor():
		_coyote_timer = coyote_time
	else:
		_coyote_timer = max(0.0, _coyote_timer - delta)

	# Input Buffering: memoriza la intención de salto si se presionó poco antes de tocar el suelo
	if Input.is_action_just_pressed("ui_accept"):
		_jump_buffer_timer = jump_buffer_time
	elif _jump_buffer_timer > 0.0:
		_jump_buffer_timer = max(0.0, _jump_buffer_timer - delta)

	# Ejecución de Salto con Coyote Time e Input Buffer
	if _jump_buffer_timer > 0.0 and (is_on_floor() or _coyote_timer > 0.0):
		velocity.y = JUMP_VELOCITY
		_jump_buffer_timer = 0.0
		_coyote_timer = 0.0
		_on_jump_performed()

	# Handle Attack
	if Input.is_action_just_pressed("attack") and _attack_timer <= 0:
		_perform_attack()

	var input_axis = Input.get_axis("ui_left", "ui_right")
	if input_axis:
		velocity.x = input_axis * SPEED
		facing_direction = 1 if input_axis > 0 else -1
	else:
		velocity.x = move_toward(velocity.x, 0, SPEED)

	var vy_before_move = velocity.y
	move_and_slide()

	# Detección de aterrizaje firme (hard landing) para screenshake y squash
	if not _was_on_floor and is_on_floor():
		_on_landed(vy_before_move)

	_was_on_floor = is_on_floor()
	_previous_velocity_y = velocity.y

	update_animations(input_axis)

func _on_jump_performed() -> void:
	_play_sfx(_sfx_jump)
	if animated_sprite_2d:
		var tween = create_tween()
		tween.tween_property(animated_sprite_2d, "scale", Vector2(0.85, 1.15), 0.06)
		tween.tween_property(animated_sprite_2d, "scale", Vector2.ONE, 0.09)

func _on_landed(fall_speed: float) -> void:
	if fall_speed >= 170.0:
		apply_screenshake(2.2, 0.12)
		_play_sfx(_sfx_land)
		if animated_sprite_2d:
			var tween = create_tween()
			tween.tween_property(animated_sprite_2d, "scale", Vector2(1.2, 0.82), 0.06)
			tween.tween_property(animated_sprite_2d, "scale", Vector2.ONE, 0.08)

func _update_timers(delta: float) -> void:
	if _hurt_timer > 0:
		_hurt_timer -= delta
		if _hurt_timer <= 0:
			is_hurt = false

	if is_invulnerable:
		_invulnerable_timer -= delta
		if animated_sprite_2d:
			var blink = int(_invulnerable_timer * 18.0) % 2 == 0
			animated_sprite_2d.modulate.a = 0.35 if blink else 1.0
		if _invulnerable_timer <= 0:
			is_invulnerable = false
			if animated_sprite_2d:
				animated_sprite_2d.modulate = Color.WHITE
			if hurtbox:
				hurtbox.set_invulnerable(false)

	if _attack_timer > 0:
		_attack_timer -= delta
		if _attack_timer <= 0 and attack_hitbox:
			attack_hitbox.monitoring = false
			attack_hitbox.monitorable = false

func _update_position_tracking(delta: float) -> void:
	if is_dead:
		return
	_sample_timer += delta
	if _sample_timer >= position_sample_interval:
		_sample_timer = 0.0
		record_current_position()

func record_current_position() -> Dictionary:
	var elapsed: float = 0.0
	var db = get_node_or_null("/root/DatabaseManager") if is_inside_tree() else null
	if db and db.has_method("get_elapsed_time"):
		elapsed = db.get_elapsed_time()

	var point = {
		"x": snappedf(global_position.x, 0.1),
		"y": snappedf(global_position.y, 0.1),
		"t": snappedf(elapsed, 0.01)
	}
	position_history.append(point)

	if db and db.has_method("record_player_position"):
		db.record_player_position(point["x"], point["y"], point["t"])

	return point

func get_position_history() -> Array[Dictionary]:
	return position_history.duplicate()

func _check_stomp_enemies() -> void:
	if not stomp_detector:
		return
	var areas = stomp_detector.get_overlapping_areas()
	for area in areas:
		if area is HurtboxClass:
			area.take_hit(stomp_detector)
			velocity.y = JUMP_VELOCITY * 0.9
			_stomp_feedback()
			break

func _stomp_feedback() -> void:
	apply_screenshake(3.5, 0.15)
	_play_sfx(_sfx_jump)
	if animated_sprite_2d:
		var tween = create_tween()
		tween.tween_property(animated_sprite_2d, "scale", Vector2(1.2, 0.8), 0.08)
		tween.tween_property(animated_sprite_2d, "scale", Vector2.ONE, 0.08)

func _perform_attack() -> void:
	_attack_timer = 0.2
	apply_screenshake(1.8, 0.1)
	if attack_hitbox:
		attack_hitbox.position.x = 12 * facing_direction
		attack_hitbox.monitoring = true
		attack_hitbox.monitorable = true
	if animated_sprite_2d:
		var tween = create_tween()
		animated_sprite_2d.modulate = Color(1.8, 1.8, 1.8, 1.0)
		tween.tween_property(animated_sprite_2d, "modulate", Color.WHITE, 0.12)

func _on_hit_received(damage: int, attacker_pos: Vector2, knockback: float) -> void:
	if is_invulnerable or is_dead:
		return
	take_damage(damage, attacker_pos, knockback)

func take_damage(amount: int, attacker_pos: Vector2 = Vector2.ZERO, knockback: float = 120.0) -> void:
	if is_invulnerable or is_dead:
		return

	current_health -= amount
	if hud:
		hud.update_health(current_health)

	_spawn_blood_vfx(attacker_pos)
	apply_screenshake(5.5, 0.25)
	_flash_damage()
	_play_sfx(_sfx_hurt)

	is_hurt = true
	_hurt_timer = 0.35
	is_invulnerable = true
	_invulnerable_timer = 1.2
	if hurtbox:
		hurtbox.set_invulnerable(true)

	var push_x = 1.0 if global_position.x >= attacker_pos.x else -1.0
	if attacker_pos == Vector2.ZERO:
		push_x = -facing_direction
	velocity = Vector2(push_x * knockback, -130.0)

	if current_health <= 0:
		die()

## Retroalimentación visual y de color al recibir daño
func _flash_damage() -> void:
	if not animated_sprite_2d:
		return
	var tween = create_tween()
	animated_sprite_2d.modulate = Color(2.5, 0.3, 0.3, 1.0)
	tween.tween_property(animated_sprite_2d, "modulate", Color.WHITE, 0.14)

## Retroalimentación al recolectar monedas / zanahorias / estrellas
func add_score(amount: int = 10) -> void:
	_on_pickup_collected(amount)

func _on_pickup_collected(_amount: int) -> void:
	_spawn_pickup_vfx()
	_play_sfx(_sfx_pickup)
	if animated_sprite_2d:
		var tween = create_tween()
		animated_sprite_2d.scale = Vector2(1.18, 1.18)
		animated_sprite_2d.modulate = Color(1.8, 1.6, 0.5, 1.0)
		tween.parallel().tween_property(animated_sprite_2d, "scale", Vector2.ONE, 0.12)
		tween.parallel().tween_property(animated_sprite_2d, "modulate", Color.WHITE, 0.15)

func _spawn_pickup_vfx() -> void:
	var effect = PickupParticleScene.instantiate()
	effect.global_position = global_position + Vector2(0, 4)
	if is_inside_tree() and get_tree() and get_tree().current_scene:
		get_tree().current_scene.add_child(effect)
	elif get_parent():
		get_parent().add_child(effect)
	else:
		add_child(effect)

func _spawn_blood_vfx(attacker_pos: Vector2) -> void:
	var blood = BloodSplatterScene.instantiate()
	blood.global_position = global_position + Vector2(0, 4)
	if is_inside_tree() and get_tree() and get_tree().current_scene:
		get_tree().current_scene.add_child(blood)
	elif get_parent():
		get_parent().add_child(blood)
	else:
		add_child(blood)

	var blood_dir: Vector2
	if attacker_pos != Vector2.ZERO:
		blood_dir = (global_position - attacker_pos).normalized()
	else:
		blood_dir = Vector2(-facing_direction, -0.7).normalized()

	blood.setup(blood_dir, true)

func die() -> void:
	is_dead = true
	is_hurt = false
	if animated_sprite_2d:
		animated_sprite_2d.play("hurt")
	if hurtbox:
		hurtbox.set_deferred("monitoring", false)
		hurtbox.set_deferred("monitorable", false)

	_spawn_blood_vfx(global_position + Vector2(0, 10))

	set_collision_mask_value(1, false)
	velocity = Vector2(0, -160.0)

	if is_inside_tree() and get_tree():
		var timer = get_tree().create_timer(1.4)
		timer.timeout.connect(func(): get_tree().change_scene_to_file("res://Scenes/GameOver.tscn"))

func update_animations(input_axis: float) -> void:
	if not animated_sprite_2d:
		return
	if input_axis < 0:
		animated_sprite_2d.flip_h = true
	elif input_axis > 0:
		animated_sprite_2d.flip_h = false

	if is_on_floor():
		if input_axis != 0:
			animated_sprite_2d.play("skip")
		else:
			animated_sprite_2d.play("idle")
	else:
		animated_sprite_2d.play("jump")

# ==============================================================================
# SISTEMA DE AUDIO PROCEDURAL (SFX RETRO)
# ==============================================================================

func _setup_sfx() -> void:
	_sfx_player = AudioStreamPlayer.new()
	_sfx_player.name = "SFXPlayer"
	_sfx_player.volume_db = -4.0
	add_child(_sfx_player)

	_sfx_jump = _create_audio_sweep(240.0, 520.0, 0.09, 0.6)
	_sfx_land = _create_audio_sweep(120.0, 50.0, 0.08, 0.7)
	_sfx_hurt = _create_noise_sweep(190.0, 70.0, 0.16, 0.8)
	_sfx_pickup = _create_chime_sfx(0.14, 0.75)

func _play_sfx(stream: AudioStream) -> void:
	if not stream or not _sfx_player:
		return
	_sfx_player.stream = stream
	_sfx_player.play()

static func _create_audio_sweep(freq_start: float, freq_end: float, duration: float, volume: float = 0.8, sample_rate: int = 22050) -> AudioStreamWAV:
	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_8_BITS
	wav.mix_rate = sample_rate
	wav.stereo = false
	var total_samples = int(duration * sample_rate)
	var data = PackedByteArray()
	data.resize(total_samples)
	var phase: float = 0.0
	for i in range(total_samples):
		var t = float(i) / float(total_samples)
		var freq = lerp(freq_start, freq_end, t)
		phase += (freq * TAU) / sample_rate
		var s = sin(phase) * (1.0 - t) * volume
		data[i] = int(clamp((s * 0.5 + 0.5) * 255.0, 0, 255))
	wav.data = data
	return wav

static func _create_noise_sweep(freq_start: float, freq_end: float, duration: float, volume: float = 0.8, sample_rate: int = 22050) -> AudioStreamWAV:
	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_8_BITS
	wav.mix_rate = sample_rate
	wav.stereo = false
	var total_samples = int(duration * sample_rate)
	var data = PackedByteArray()
	data.resize(total_samples)
	var phase: float = 0.0
	for i in range(total_samples):
		var t = float(i) / float(total_samples)
		var freq = lerp(freq_start, freq_end, t)
		phase += (freq * TAU) / sample_rate
		var s = (sin(phase) * 0.7 + (randf() * 2.0 - 1.0) * 0.3) * (1.0 - t) * volume
		data[i] = int(clamp((s * 0.5 + 0.5) * 255.0, 0, 255))
	wav.data = data
	return wav

static func _create_chime_sfx(duration: float = 0.14, volume: float = 0.75, sample_rate: int = 22050) -> AudioStreamWAV:
	var total_samples = int(duration * sample_rate)
	var half_samples = int(total_samples * 0.45)
	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_8_BITS
	wav.mix_rate = sample_rate
	wav.stereo = false
	var data = PackedByteArray()
	data.resize(total_samples)
	var phase: float = 0.0
	for i in range(total_samples):
		var freq = 880.0 if i < half_samples else 1320.0
		var t = float(i) / float(half_samples) if i < half_samples else float(i - half_samples) / float(total_samples - half_samples)
		phase += (freq * TAU) / sample_rate
		var s = sin(phase) * (1.0 - t * 0.55) * volume
		data[i] = int(clamp((s * 0.5 + 0.5) * 255.0, 0, 255))
	wav.data = data
	return wav
