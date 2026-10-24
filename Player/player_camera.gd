extends Camera2D
class_name PlayerCamera

var _shake_intensity: float = 0.0
var _shake_duration: float = 0.0
var _shake_timer: float = 0.0

func _process(delta: float) -> void:
	if _shake_timer > 0.0:
		_shake_timer -= delta
		if _shake_timer <= 0.0:
			offset = Vector2.ZERO
			_shake_intensity = 0.0
		else:
			var progress = _shake_timer / _shake_duration
			var current_shake = _shake_intensity * progress
			offset = Vector2(
				randf_range(-current_shake, current_shake),
				randf_range(-current_shake, current_shake)
			)

## Método reutilizable para vibración de cámara
func apply_screenshake(intensity: float = 4.0, duration: float = 0.2) -> void:
	_shake_intensity = max(_shake_intensity, intensity)
	_shake_duration = max(_shake_duration, duration)
	_shake_timer = duration
