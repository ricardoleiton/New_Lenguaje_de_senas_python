# Lengua de Señas — Holistic Unificado

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Versión](https://img.shields.io/badge/versión-0.2.0-brightgreen.svg)
![Estado](https://img.shields.io/badge/estado-activo-brightgreen.svg)
![Modelo](https://img.shields.io/badge/modelo-LSTM%20unificado-red.svg)
![Auth](https://img.shields.io/badge/auth-RBAC%20%2B%20bcrypt-orange.svg)
![Licencia](https://img.shields.io/badge/licencia-MIT-blue.svg)

Reconocimiento de gestos de lengua de señas para **letras, números y palabras**
usando **MediaPipe Holistic** para landmarks y **LSTM Keras** para
clasificación de secuencias.

A partir de **v0.2.0** la aplicación incorpora **roles y login** con dos perfiles
iniciales (Profesor / Estudiante), escalables por configuración.

---

## Estado actual

- ✅ Pipeline end-to-end funcional: captura → entrenamiento → predicción.
- ✅ Sistema de roles (RBAC) con login y audit log.
- ✅ Interfaz gráfica de escritorio (`gui_app.py`) y acceso Windows (`abrir_app.bat`).
- ✅ Captura de letras, números y palabras completas.
- ✅ Selección de cámara cuando hay más de un dispositivo instalado.
- ✅ Documentación técnica centralizada en `docs/`.
- ✅ Modelo actual entrenado con 8 clases: `1`, `2`, `a`, `b`, `c`, `d`,
  `hola`, `trabajar`.

---

## Roles disponibles

| Rol         | Capturar | Entrenar | Predecir | Gestionar usuarios |
|-------------|:--------:|:--------:|:--------:|:------------------:|
| `profesor`  |    ✅    |    ✅    |    ✅    |        ✅          |
| `estudiante`|          |          |    ✅    |                    |

> El catálogo de roles vive en `config/roles.json`. Sumar un rol nuevo (por
> ejemplo "asistente" con captura+predicción) **no requiere cambios de código**:
> editar el JSON y listo. Ver `docs/ROLES.md`.

---

## Estructura del proyecto

```
Lenguaje_de_senas_python/
├── main.py                  # Login + menú dinámico filtrado por permisos
├── gui_app.py               # Entrada de compatibilidad para la GUI
├── abrir_app.bat            # Launcher Windows para abrir la GUI
├── version.py               # __version__
├── pyproject.toml
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── auth/                    # Autenticación, RBAC, sesión, audit
├── core/                    # Configuración + procesamiento de landmarks
├── gui/                     # App Tkinter, tema, salida y pantallas
├── services/                # Servicios de captura, entrenamiento y predicción
├── vision/                  # Cámara + dibujo + GIFs
├── ml/                      # Modelo LSTM + carga de dataset
├── workflows/               # Permisos + orquestación CLI/GUI
├── config/                  # roles.json + users.json (gitignored)
│
├── data/secuencias/<clase>/ # Dataset .npy
├── gifs/<clase>.gif         # Referencia visual
├── models/                  # modelo_lstm.h5 + etiquetas.pkl + history.json
├── logs/audit.log           # Auditoría (gitignored)
└── docs/                    # ARCHITECTURE, SECURITY, ROLES, TROUBLESHOOTING,
                             # DECISIONS, CHANGELOG, DEVELOPMENT
```

Detalle completo en [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Requisitos

- Python **3.10+**
- Webcam funcional
- Sistema operativo: Windows / Linux / macOS

---

## Instalación

```bash
git clone <url-del-repo>
cd Lenguaje_de_senas_python
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### Nota para Windows

Si al instalar dependencias `bcrypt` falla porque Python intenta compilarlo
desde fuente, instalá la versión binaria precompilada:

```powershell
pip install --only-binary :all: "bcrypt~=4.1"
```

Después volvé a correr `pip install -r requirements.txt` para asegurarte
del resto. Detalle en [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md).

---

## Primer uso

### Interfaz gráfica recomendada

En Windows, abrí la aplicación con doble click en:

```text
abrir_app.bat
```

También podés ejecutarla manualmente:

```powershell
.\.venv\Scripts\python.exe gui_app.py
```

La consola queda como alternativa de soporte:

```powershell
.\.venv\Scripts\python.exe main.py
```

Desde el panel principal podés entrar a **Seleccionar cámara** para elegir qué
dispositivo usar cuando el equipo tenga más de una webcam instalada.

En el primer arranque, la app detecta que no hay usuarios y pide crear el
primer profesor. En GUI se muestra un formulario; en consola se ve así:

```
============================================================
  PRIMERA EJECUCIÓN — CREAR PROFESOR INICIAL
============================================================

Nuevo username (3-30 caracteres, a-z 0-9 _): ricardo
Password (mín. 8 caracteres, al menos 1 dígito): ********
Repetir password: ********

✅ Usuario 'ricardo' creado con rol 'profesor'
```

A partir del segundo arranque, la app pide login normal.

---

## Uso

### Como profesor

```
- Seleccionar cámara
- Capturar letra, número o palabra  # elegir tipo y valor, graba 10 secuencias
- Entrenar modelo LSTM              # entrena con los datos disponibles
- Predicción en tiempo real
- Gestionar usuarios                # ABM de usuarios, cambio de rol/password
- Cambiar mi contraseña
- Cerrar sesión
```

### Como estudiante

```
- Seleccionar cámara
- Predicción en tiempo real
- Cambiar mi contraseña
- Cerrar sesión
```

---

## Modelo y datos

- **Features por frame:** 147 (2 manos × 21 puntos × 3 + 2 hombros × 3 + 5 puntos faciales × 3).
- **Frames por secuencia:** 10.
- **Secuencias por clase:** 10.
- **Arquitectura:** `LSTM(64, return_sequences) → BatchNorm → LSTM(32) → Dropout(0.3) → Dense(64, relu) → Dense(N, softmax)`.
- **Optimizador:** Adam con `EarlyStopping`, `ReduceLROnPlateau`, `ModelCheckpoint`.
- **Split:** 70/15/15 estratificado (con fallback a 80/20 si hay pocas muestras).

Dataset/modelo actual: 8 clases (`1`, `2`, `a`, `b`, `c`, `d`, `hola`,
`trabajar`) × 10 secuencias = 80 secuencias. Cada secuencia nueva guarda 10
frames. Las capturas antiguas de 30 frames se remuestrean automáticamente a 10
frames al entrenar.

---

## Versionado

Esta es la versión **0.2.0**. Histórico completo en
[`docs/CHANGELOG.md`](docs/CHANGELOG.md).

- v0.1.0: versión inicial Holistic Unificada.
- v0.2.0: sistema de roles, login, audit, reorganización en módulos.

---

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Estructura, capas, flujos de datos |
| [LEVANTAMIENTO_NECESIDADES.md](docs/LEVANTAMIENTO_NECESIDADES.md) | Necesidad, problema, alcance y requisitos |
| [SECURITY.md](docs/SECURITY.md)         | Modelo de amenazas, auth, audit |
| [ROLES.md](docs/ROLES.md)               | Catálogo de roles y cómo escalar |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Errores comunes y soluciones |
| [DECISIONS.md](docs/DECISIONS.md)       | ADRs (decisiones de arquitectura) |
| [CHANGELOG.md](docs/CHANGELOG.md)       | Histórico de versiones |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md)   | Guía para contribuir / extender |
| [TESTING.md](docs/TESTING.md)           | Tests automatizados y cómo ejecutarlos |
| [RELEVAMIENTO_TECNICO.md](docs/RELEVAMIENTO_TECNICO.md) | Relevamiento técnico inicial (v0.1.0) |

---

## Licencia

MIT — ver [LICENSE](LICENSE).

---

## Autores

- Ricardo Leitón
