# Sunny Land Forest (Godot 4)

## Parámetros Técnicos de Jugabilidad y Game Feel

A continuación se detallan las constantes y valores configurados en el script del personaje ([`player.gd`](file:///c:/Users/MGOG0/Downloads/SunnyLandForestGodot-20260922T054110Z-1-001/SunnyLandForestGodot/Player/player.gd)) y la cámara ([`player_camera.gd`](file:///c:/Users/MGOG0/Downloads/SunnyLandForestGodot-20260922T054110Z-1-001/SunnyLandForestGodot/Player/player_camera.gd)):

### 1. Mecánicas de Salto y Plataformeo
| Parámetro | Variable | Valor | Descripción |
| :--- | :--- | :--- | :--- |
| **Input Buffering** | `jump_buffer_time` | `0.14 s` (140 ms) | Margen para registrar y ejecutar automáticamente el salto si se presiona la tecla antes de tocar el suelo. |
| **Coyote Time** | `coyote_time` | `0.14 s` (140 ms) | Tiempo de gracia para permitir saltar tras abandonar el borde de una plataforma en caída. |
| **Velocidad de Salto** | `JUMP_VELOCITY` | `-200.0 px/s` | Impulso vertical del salto. |
| **Velocidad de Movimiento** | `SPEED` | `110.0 px/s` | Velocidad horizontal de desplazamiento. |
| **Gravedad** | `gravity` | `300.0 px/s²` | Aceleración vertical hacia abajo. |

---

### 2. Vibración de Pantalla (Screenshake)
Función reutilizable: `apply_screenshake(intensity, duration)` en [`Camera2D`](file:///c:/Users/MGOG0/Downloads/SunnyLandForestGodot-20260922T054110Z-1-001/SunnyLandForestGodot/Player/player_camera.gd). Modula el `offset` de cámara con decaimiento lineal sin afectar el seguimiento (`position_smoothing`).

| Evento | Intensidad (`px`) | Duración (`s`) | Condición de Activación |
| :--- | :---: | :---: | :--- |
| **Daño recibido** | `5.5` | `0.25 s` | Al recibir un impacto de enemigo o trampa (`take_damage`). |
| **Pisotón sobre enemigo** | `3.5` | `0.15 s` | Al impactar y rebotar sobre la cabeza de un enemigo (`_stomp_feedback`). |
| **Aterrizaje fuerte** | `2.2` | `0.12 s` | Al tocar suelo tras caer con velocidad vertical $\ge 170.0 \text{ px/s}$. |
| **Ataque cuerpo a cuerpo** | `1.8` | `0.10 s` | Al ejecutar un ataque frontal con `attack_hitbox`. |

---

### 3. Retroalimentación Visual (Squash & Stretch y Destellos)
| Acción | Transformación / Color | Duración |
| :--- | :--- | :--- |
| **Despegue de Salto** | Escala `(0.85, 1.15)` $\rightarrow$ `(1.0, 1.0)` | `0.06 s` + `0.09 s` |
| **Aterrizaje Fuerte** | Escala `(1.20, 0.82)` $\rightarrow$ `(1.0, 1.0)` | `0.06 s` + `0.08 s` |
| **Recolección de Ítem** | Escala `(1.18, 1.18)` y modulación `Color(1.8, 1.6, 0.5)` | `0.12 s` / `0.15 s` |
| **Destello de Daño** | Modulación `Color(2.5, 0.3, 0.3)` $\rightarrow$ `Color.WHITE` | `0.14 s` |
| **Partículas de Ítem** | CPUParticles2D (12 partículas, velocidad `30-70`, vida `0.45 s`) | `0.45 s` (one-shot) |

---

### 4. Audio Procedural Retro (AudioStreamWAV a 22.05 kHz)
Generados dinámicamente en código sin requerir archivos de audio externos:
* **Salto:** Barrido ascendente `240 Hz` $\rightarrow$ `520 Hz` (`0.09 s`).
* **Recolección (Zanahoria/Estrella):** Doble tono armónico `880 Hz` + `1320 Hz` (`0.14 s`).
* **Daño:** Barrido descendente con ruido blanco `190 Hz` $\rightarrow$ `70 Hz` (`0.16 s`).
* **Aterrizaje:** Impacto grave `120 Hz` $\rightarrow$ `50 Hz` (`0.08 s`).
