extends Node

## DatabaseManager
## Administrador de Base de Datos SQLite para Sunny Land Forest
## Gestiona la conexión a SQLite, tablas relacionales e inserción de sesiones de juego y coordenadas.

signal session_saved(session_data: Dictionary)

const DB_FILE_PATH: String = "user://game_database.db"

var db: SQLite = null
var is_initialized: bool = false

# Variables de seguimiento de la sesión actual
var active_user_id: int = 1
var current_level_name: String = "Nivel 1"
var level_start_ticks: int = 0
var level_coins_collected: int = 0
var is_tracking: bool = false
var last_saved_session: Dictionary = {}

# Arreglo de posiciones (x, y) de la partida actual
var current_positions: Array[Dictionary] = []

func _ready() -> void:
	init_database()

## Inicializa la base de datos SQLite y crea el esquema relacional
func init_database() -> void:
	if is_initialized:
		return
		
	db = SQLite.new()
	db.path = DB_FILE_PATH
	db.foreign_keys = true
	
	if not db.open_db():
		printerr("[DatabaseManager] Error al abrir la base de datos SQLite en: ", DB_FILE_PATH)
		return
		
	# Habilitar claves foráneas
	db.query("PRAGMA foreign_keys = ON;")
	
	# 1. Tabla de usuarios/jugadores (Padre en la relación)
	var sql_users = """
	CREATE TABLE IF NOT EXISTS usuarios (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		nombre TEXT NOT NULL UNIQUE,
		fecha_creacion TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
	);
	"""
	db.query(sql_users)
	
	# 2. Tabla relacional de sesiones de juego
	# Almacena: ID, usuario_id, tiempo_transcurrido, monedas_recolectadas, nivel, fecha y coordenadas (JSON)
	var sql_sessions = """
	CREATE TABLE IF NOT EXISTS sesiones_juego (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		usuario_id INTEGER NOT NULL DEFAULT 1,
		tiempo_transcurrido REAL NOT NULL,
		monedas_recolectadas INTEGER NOT NULL,
		nivel TEXT NOT NULL,
		fecha TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
		coordenadas TEXT DEFAULT '[]',
		FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
	);
	"""
	db.query(sql_sessions)
	
	# Migración: Asegurar que la columna 'coordenadas' exista si la tabla ya había sido creada antes
	db.query("PRAGMA table_info(sesiones_juego);")
	var has_coordenadas = false
	for col in db.query_result:
		if col.get("name") == "coordenadas":
			has_coordenadas = true
			break
	if not has_coordenadas:
		db.query("ALTER TABLE sesiones_juego ADD COLUMN coordenadas TEXT DEFAULT '[]';")
		
	# 3. Tabla relacional de posiciones del recorrido del jugador
	# Permite almacenar y consultar cada muestra individual (x, y) vinculada por clave foránea a la sesión
	var sql_positions = """
	CREATE TABLE IF NOT EXISTS posiciones_sesion (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		sesion_id INTEGER NOT NULL,
		posicion_x REAL NOT NULL,
		posicion_y REAL NOT NULL,
		tiempo_marca REAL NOT NULL,
		FOREIGN KEY (sesion_id) REFERENCES sesiones_juego(id) ON DELETE CASCADE
	);
	"""
	db.query(sql_positions)
	
	# Asegurar usuario por defecto para las sesiones
	db.query("INSERT OR IGNORE INTO usuarios (id, nombre) VALUES (1, 'Jugador Principal');")
	
	is_initialized = true
	var real_path = ProjectSettings.globalize_path(DB_FILE_PATH)
	print("[DatabaseManager] Base de datos SQLite inicializada exitosamente.")
	print("[DatabaseManager] Ubicación del archivo de base de datos: ", real_path)

## Inicia el cronómetro, conteo de monedas y registro de posiciones para un nivel
func start_level_tracking(level_name: String = "") -> void:
	if level_name != "":
		current_level_name = level_name
	level_start_ticks = Time.get_ticks_msec()
	level_coins_collected = 0
	current_positions.clear()
	is_tracking = true
	print("[DatabaseManager] Seguimiento iniciado para: '%s'" % current_level_name)

## Registra una moneda recolectada en la sesión activa
func record_coin() -> void:
	level_coins_collected += 1

## Registra periódicamente una posición (x, y) del jugador
func record_player_position(x: float, y: float, t: float = -1.0) -> void:
	var time_val = t if t >= 0 else get_elapsed_time()
	current_positions.append({
		"x": snappedf(x, 0.1),
		"y": snappedf(y, 0.1),
		"t": snappedf(time_val, 0.01)
	})

## Obtiene las posiciones registradas en la partida en curso
func get_current_positions() -> Array[Dictionary]:
	return current_positions.duplicate()

## Obtiene el tiempo transcurrido en segundos desde el inicio del nivel
func get_elapsed_time() -> float:
	if not is_tracking or level_start_ticks == 0:
		return 0.0
	var now = Time.get_ticks_msec()
	return (now - level_start_ticks) / 1000.0

## Inserta una nueva sesión y sus posiciones en la base de datos relacional
func insert_session(usuario_id: int, nivel: String, tiempo_transcurrido: float, monedas: int, coords: Array = []) -> Dictionary:
	if not is_initialized or db == null:
		init_database()
		
	# Redondear tiempo a 2 decimales
	var tiempo_redondeado: float = snappedf(tiempo_transcurrido, 0.01)
	
	# Usar las coordenadas pasadas o las recopiladas por DatabaseManager
	var coords_to_save: Array = coords if not coords.is_empty() else current_positions
	var json_coords: String = JSON.stringify(coords_to_save).replace("'", "''")
	
	# 1. Insertar sesión principal
	var insert_sql = """
	INSERT INTO sesiones_juego (usuario_id, tiempo_transcurrido, monedas_recolectadas, nivel, fecha, coordenadas)
	VALUES (%d, %.2f, %d, '%s', datetime('now', 'localtime'), '%s');
	""" % [usuario_id, tiempo_redondeado, monedas, nivel.replace("'", "''"), json_coords]
	
	var success = db.query(insert_sql)
	if not success:
		printerr("[DatabaseManager] Error al ejecutar inserción en sesiones_juego: ", db.error_message)
		return {}
		
	var new_id = db.get_last_insert_rowid()
	
	# 2. Insertar cada coordenada en la tabla relacional posiciones_sesion
	if not coords_to_save.is_empty():
		for pt in coords_to_save:
			var px: float = float(pt.get("x", 0.0))
			var py: float = float(pt.get("y", 0.0))
			var pt_t: float = float(pt.get("t", 0.0))
			db.query("INSERT INTO posiciones_sesion (sesion_id, posicion_x, posicion_y, tiempo_marca) VALUES (%d, %.2f, %.2f, %.2f);" % [
				new_id, px, py, pt_t
			])
	
	# 3. Consultar el registro insertado con los datos relacionales
	var select_sql = """
	SELECT s.id, u.nombre AS usuario, s.nivel, s.tiempo_transcurrido, s.monedas_recolectadas, s.fecha, s.coordenadas
	FROM sesiones_juego s
	JOIN usuarios u ON s.usuario_id = u.id
	WHERE s.id = %d;
	""" % new_id
	
	db.query(select_sql)
	var session_data: Dictionary = {}
	if db.query_result.size() > 0:
		session_data = db.query_result[0]
	else:
		session_data = {
			"id": new_id,
			"usuario_id": usuario_id,
			"nivel": nivel,
			"tiempo_transcurrido": tiempo_redondeado,
			"monedas_recolectadas": monedas,
			"fecha": Time.get_datetime_string_from_system(),
			"coordenadas": JSON.stringify(coords_to_save)
		}
		
	last_saved_session = session_data
	session_saved.emit(session_data)
	print("[DatabaseManager] ¡Sesión registrada con éxito! ID: #%s | Nivel: %s | Tiempo: %.2fs | Monedas: %d | Coordenadas: %d muestras" % [
		session_data.get("id"),
		session_data.get("nivel"),
		session_data.get("tiempo_transcurrido"),
		session_data.get("monedas_recolectadas"),
		coords_to_save.size()
	])
	return session_data

## Finaliza el nivel actual y guarda la sesión automáticamente junto con las coordenadas
func finish_level_and_save(level_name: String = "", override_coins: int = -1, coords: Array = []) -> Dictionary:
	var final_level = level_name if level_name != "" else current_level_name
	var elapsed = get_elapsed_time()
	var coins = override_coins if override_coins >= 0 else level_coins_collected
	
	# Detener seguimiento
	is_tracking = false
	
	return insert_session(active_user_id, final_level, elapsed, coins, coords)

## Obtiene todas las sesiones registradas con información del usuario
func get_all_sessions(limit: int = 50) -> Array:
	if not is_initialized or db == null:
		init_database()
		
	var sql = """
	SELECT s.id, u.nombre AS usuario, s.nivel, s.tiempo_transcurrido, s.monedas_recolectadas, s.fecha, s.coordenadas
	FROM sesiones_juego s
	JOIN usuarios u ON s.usuario_id = u.id
	ORDER BY s.id DESC
	LIMIT %d;
	""" % limit
	
	db.query(sql)
	return db.query_result.duplicate()

## Consulta las posiciones relacionales guardadas para una sesión específica
func get_session_positions(session_id: int) -> Array:
	if not is_initialized or db == null:
		init_database()
		
	var sql = """
	SELECT posicion_x, posicion_y, tiempo_marca
	FROM posiciones_sesion
	WHERE sesion_id = %d
	ORDER BY id ASC;
	""" % session_id
	
	db.query(sql)
	return db.query_result.duplicate()

## Obtiene la última sesión guardada
func get_last_session() -> Dictionary:
	if not last_saved_session.is_empty():
		return last_saved_session
		
	var sessions = get_all_sessions(1)
	if sessions.size() > 0:
		last_saved_session = sessions[0]
		return last_saved_session
	return {}

## Formatea segundos a texto legible "MM:SS.ss"
static func format_time(seconds: float) -> String:
	var total_sec: int = int(seconds)
	var mins: int = total_sec / 60
	var secs: int = total_sec % 60
	var millis: int = int((seconds - total_sec) * 100)
	return "%02d:%02d.%02d" % [mins, secs, millis]

## Cierra la base de datos limpiamente
func close_database() -> void:
	if db and is_initialized:
		db.close_db()
		is_initialized = false

func _exit_tree() -> void:
	close_database()
