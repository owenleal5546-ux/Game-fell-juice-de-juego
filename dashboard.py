#!/usr/bin/env python3
"""
Sunny Land Forest - SQLite Game Dashboard
Lee la base de datos de sesiones del juego en Godot y despliega una interfaz
web local en http://localhost:5000 para consultar y filtrar los resultados,
incluyendo el historial de coordenadas (x, y) de la trayectoria del jugador.
"""

import os
import sys
import json
import sqlite3
from typing import Dict, Any, List, Optional
from flask import Flask, render_template, jsonify, request

app = Flask(__name__, template_folder="templates")

def get_database_path() -> str:
    """
    Determina la ruta de la base de datos SQLite del juego.
    1. Argumento de línea de comandos si se especifica.
    2. Carpeta app_userdata estándar de Godot en Windows (%APPDATA%/Godot/app_userdata/...).
    3. Archivo local en el directorio actual.
    """
    if len(sys.argv) > 1 and sys.argv[1].endswith(".db"):
        return os.path.abspath(sys.argv[1])
        
    appdata = os.environ.get("APPDATA")
    if appdata:
        godot_db_path = os.path.join(
            appdata,
            "Godot",
            "app_userdata",
            "Sunny Land Forest Godot",
            "game_database.db"
        )
        if os.path.exists(godot_db_path):
            return godot_db_path
            
    # Fallback local o crear ruta si no existe
    local_db = os.path.abspath("game_database.db")
    if os.path.exists(local_db):
        return local_db
        
    if appdata:
        return os.path.join(
            appdata,
            "Godot",
            "app_userdata",
            "Sunny Land Forest Godot",
            "game_database.db"
        )
        
    return local_db

DB_PATH = get_database_path()

def get_db_connection() -> Optional[sqlite3.Connection]:
    """Establece conexión con la base de datos SQLite con timeout seguro."""
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                fecha_creacion TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );
        """)
        conn.execute("""
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
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posiciones_sesion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sesion_id INTEGER NOT NULL,
                posicion_x REAL NOT NULL,
                posicion_y REAL NOT NULL,
                tiempo_marca REAL NOT NULL,
                FOREIGN KEY (sesion_id) REFERENCES sesiones_juego(id) ON DELETE CASCADE
            );
        """)
        conn.execute("INSERT OR IGNORE INTO usuarios (id, nombre) VALUES (1, 'Jugador Principal');")
        conn.commit()
        conn.row_factory = sqlite3.Row
        return conn

    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_sessions_data() -> Dict[str, Any]:
    """Consulta todas las sesiones y calcula métricas clave."""
    try:
        conn = get_db_connection()
        if not conn:
            return {"sessions": [], "stats": {}, "db_path": DB_PATH}

        cur = conn.cursor()
        
        # Asegurar columnas si se conecta a una base existente anterior
        try:
            cur.execute("PRAGMA table_info(sesiones_juego)")
            cols = [c["name"] for c in cur.fetchall()]
            if "coordenadas" not in cols:
                cur.execute("ALTER TABLE sesiones_juego ADD COLUMN coordenadas TEXT DEFAULT '[]'")
                conn.commit()
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS posiciones_sesion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sesion_id INTEGER NOT NULL,
                    posicion_x REAL NOT NULL,
                    posicion_y REAL NOT NULL,
                    tiempo_marca REAL NOT NULL,
                    FOREIGN KEY (sesion_id) REFERENCES sesiones_juego(id) ON DELETE CASCADE
                );
            """)
            conn.commit()
        except Exception as mig_err:
            print("[Migración]:", mig_err)

        # Consultar sesiones con JOIN a usuarios y conteo de posiciones
        query = """
            SELECT 
                s.id,
                COALESCE(u.nombre, 'Jugador') AS usuario,
                s.nivel,
                ROUND(s.tiempo_transcurrido, 2) AS tiempo_transcurrido,
                s.monedas_recolectadas,
                s.fecha,
                COALESCE(s.coordenadas, '[]') AS coordenadas_json,
                (SELECT COUNT(*) FROM posiciones_sesion p WHERE p.sesion_id = s.id) AS num_posiciones
            FROM sesiones_juego s
            LEFT JOIN usuarios u ON s.usuario_id = u.id
            ORDER BY s.id DESC
        """
        cur.execute(query)
        raw_rows = cur.fetchall()
        rows = []
        for r in raw_rows:
            d = dict(r)
            # Parsear coordenadas JSON para mayor facilidad de uso en frontend
            try:
                coords = json.loads(d.get("coordenadas_json") or "[]")
            except Exception:
                coords = []
            d["coordenadas"] = coords
            d["total_puntos"] = max(d.get("num_posiciones", 0), len(coords))
            del d["coordenadas_json"]
            rows.append(d)

        # Calcular estadísticas globales
        total_sessions = len(rows)
        total_coins = sum(r["monedas_recolectadas"] for r in rows) if rows else 0
        avg_coins = (total_coins / total_sessions) if total_sessions > 0 else 0.0
        avg_time = (sum(r["tiempo_transcurrido"] for r in rows) / total_sessions) if total_sessions > 0 else 0.0
        total_points_tracked = sum(r["total_puntos"] for r in rows) if rows else 0
        
        # Mejor tiempo (más rápido > 0s)
        best_time_overall = None
        best_level = None
        valid_times = [r for r in rows if r["tiempo_transcurrido"] > 0]
        if valid_times:
            fastest_run = min(valid_times, key=lambda x: x["tiempo_transcurrido"])
            best_time_overall = fastest_run["tiempo_transcurrido"]
            best_level = fastest_run["nivel"]

        # Estadísticas agrupadas por nivel
        level_stats: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            lvl = r["nivel"]
            if lvl not in level_stats:
                level_stats[lvl] = {
                    "count": 0,
                    "total_coins": 0,
                    "best_time": r["tiempo_transcurrido"]
                }
            level_stats[lvl]["count"] += 1
            level_stats[lvl]["total_coins"] += r["monedas_recolectadas"]
            if r["tiempo_transcurrido"] > 0 and r["tiempo_transcurrido"] < level_stats[lvl]["best_time"]:
                level_stats[lvl]["best_time"] = r["tiempo_transcurrido"]

        conn.close()

        stats = {
            "total_sessions": total_sessions,
            "total_coins": total_coins,
            "avg_coins": round(avg_coins, 1),
            "avg_time": round(avg_time, 2),
            "best_time_overall": best_time_overall,
            "best_level": best_level,
            "total_points_tracked": total_points_tracked,
            "levels": level_stats
        }

        return {
            "sessions": rows,
            "stats": stats,
            "db_path": DB_PATH
        }
    except Exception as e:
        print(f"[Error leyendo SQLite]: {e}")
        return {"sessions": [], "stats": {}, "db_path": DB_PATH, "error": str(e)}

@app.route("/")
def index():
    """Ruta principal que despliega el dashboard interactivo."""
    return render_template("dashboard.html", db_path=DB_PATH)

@app.route("/api/sessions")
def api_sessions():
    """Endpoint REST que devuelve los datos y estadísticas en formato JSON."""
    data = fetch_sessions_data()
    return jsonify(data)

@app.route("/api/stats")
def api_stats():
    """Endpoint REST con las métricas consolidadas."""
    data = fetch_sessions_data()
    return jsonify(data.get("stats", {}))

@app.route("/api/session/<int:session_id>/positions")
def api_session_positions(session_id: int):
    """Endpoint REST para consultar las coordenadas de una partida desde la tabla relacional posiciones_sesion."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT posicion_x, posicion_y, tiempo_marca
            FROM posiciones_sesion
            WHERE sesion_id = ?
            ORDER BY id ASC
        """, (session_id,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return jsonify({"session_id": session_id, "total": len(rows), "positions": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = 5000
    host = "127.0.0.1"
    
    print("\n" + "="*60)
    print("[*] SUNNY LAND FOREST - DASHBOARD DE PARTIDAS SQLITE")
    print("="*60)
    print(f"[*] Base de datos:  {DB_PATH}")
    print(f"[*] Servidor web:   http://localhost:{port}")
    print(f"[*] API REST:       http://localhost:{port}/api/sessions")
    print("="*60 + "\n")
    
    app.run(host=host, port=port, debug=False)
