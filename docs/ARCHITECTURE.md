# Arquitectura

> Versión documentada: **0.2.0**
> Última actualización: 2026-05-01

## 1. Visión general

Aplicación local de escritorio para reconocimiento de gestos de lengua de señas
basada en MediaPipe Holistic + LSTM Keras. La interfaz recomendada es
`gui_app.py` (Tkinter), con `main.py` como alternativa de consola para soporte.
Funciona localmente sobre webcam, sin servicios remotos.

## 2. Estructura de directorios

```
Lenguaje_de_senas_python/
├── main.py                  # Entrada CLI: login + menú dinámico
├── gui_app.py               # Interfaz gráfica Tkinter
├── abrir_app.bat            # Launcher Windows de la GUI
├── version.py               # Fuente única de __version__
├── pyproject.toml           # Metadata del proyecto
├── requirements.txt         # Dependencias runtime
├── README.md
├── LICENSE                  # MIT
├── .gitignore
│
├── auth/                    # Autenticación, RBAC, sesión, audit
│   ├── crypto.py            #   bcrypt hash/verify
│   ├── rbac.py              #   carga roles.json, requerir(permiso, rol)
│   ├── session.py           #   usuario logueado en memoria
│   ├── users.py             #   CRUD users.json
│   ├── audit.py             #   audit log
│   └── login.py             #   bootstrap + loop de login
│
├── core/                    # Configuración + landmarks
│   ├── config.py            #   dataclass frozen Config
│   ├── console.py           #   salida UTF-8 + helpers de stderr nativo
│   ├── ui.py                #   formato común de consola/logs
│   └── landmarks.py         #   extract / normalize / validate
│
├── vision/                  # Cámara + dibujo + GIF + overlays
│   ├── camera.py
│   └── overlay.py
│
├── ml/                      # Modelo + carga de dataset
│   ├── model.py             #   construir_modelo (LSTM)
│   └── data_io.py           #   cargar_datos
│
├── workflows/               # Flujos de la app
│   ├── capturar.py
│   ├── entrenar.py
│   ├── predecir.py
│   └── gestion_usuarios.py
│
├── config/
│   ├── roles.json           # Definición de roles y permisos (versionado)
│   └── users.json           # Usuarios + hashes (gitignored)
│
├── data/secuencias/<clase>/ # Dataset: .npy de (10, 147) por muestra
├── gifs/<clase>.gif         # GIF de referencia por clase
├── models/                  # modelo_lstm.h5 + etiquetas.pkl + history.json
├── logs/audit.log           # Auditoría (gitignored)
└── docs/                    # Documentación técnica
```

## 3. Flujo de datos

### 3.1. Captura (workflow `capturar`)

```
Usuario  →  cámara  →  MediaPipe Holistic  →  extract_landmarks(147)
        →  normalize  →  validate  →  cuenta regresiva inicial
        →  buffer 10 frames × 10 secuencias por clase
        →  np.save(data/secuencias/<clase>/<clase>_<i>.npy)
        →  generar_gif(gifs/<clase>.gif)  [primera muestra]
```

### 3.2. Entrenamiento (workflow `entrenar`)

```
data/secuencias/*  →  cargar_datos  →  X (N, 10, 147), y (N,), etiquetas
        →  train_test_split estratificado (70/15/15)
        →  LSTM(64, return_sequences) → BatchNorm → LSTM(32) → Dropout(0.3)
           → Dense(64, relu) → Dense(num_clases, softmax)
        →  fit + EarlyStopping + ReduceLROnPlateau + ModelCheckpoint
        →  classification_report + matriz de confusión
        →  save modelo_lstm.h5 + etiquetas.pkl + history.json
```

### 3.3. Predicción (workflow `predecir`)

```
cámara  →  Holistic  →  extract  →  normalize  →  validate
        →  buffer deque(maxlen=10)
        →  cuando se llena: model.predict → idx, confianza
        →  pred_buffer deque(maxlen=3): consenso 2/3 + confianza > 0.6
        →  mostrar etiqueta en ventana de cámara + GIF en panel de referencia
```

La predicción abre dos ventanas desde el inicio: cámara en vivo y referencia
guardada. El panel de referencia permanece vacío hasta que se detecta una clase.

### 3.4. Selección de cámara

```
GUI/CLI  →  discover_cameras()  →  set_selected_camera_index(index)
        →  setup_camera() usa el índice seleccionado en captura/predicción
```

### 3.5. Autenticación

```
main.py
  ├── existe_usuarios()? NO  →  bootstrap_inicial (wizard)
  └── login_loop:
        ├── input(username, password)
        ├── autenticar  →  bcrypt.checkpw
        ├── OK    →  set_usuario(Usuario(username, rol))  →  log "login"
        └── FAIL  →  log "login FAIL"  →  delay incremental (1, 2, 4, 8, 16s)
```

## 4. Modelo de permisos

| Permiso              | Descripción                                  |
|----------------------|----------------------------------------------|
| `predecir`           | Ejecutar predicción en tiempo real           |
| `capturar`           | Grabar nuevas secuencias para alimentar el dataset |
| `entrenar`           | Reentrenar el modelo con el dataset actual   |
| `gestionar_usuarios` | Listar/crear/eliminar/cambiar rol de usuarios |

| Rol         | Permisos                                                      |
|-------------|---------------------------------------------------------------|
| estudiante  | `predecir`                                                    |
| profesor    | `capturar`, `entrenar`, `predecir`, `gestionar_usuarios`      |

Ver `docs/ROLES.md` para el detalle de cómo agregar un rol nuevo.

## 5. Decisiones de diseño clave

- **Estructura por dominio funcional** (auth/core/vision/ml/workflows): facilita
  testing y comprensión sin necesidad de paquete instalable.
- **`core.config.config` como singleton inmutable** (`@dataclass(frozen=True)`):
  cualquier override pasa por código, no por mutación en runtime.
- **Defense in depth**: cada workflow llama `requerir(permiso, rol)` al inicio,
  además de que el menú ya filtra opciones. Si alguien importa el módulo
  directamente, el bloqueo se mantiene.
- **Sesión solo en memoria**: cada arranque de `main.py` requiere login. No
  hay tokens persistidos.
- **`config/users.json` gitignored**: no se versionan hashes de password.
- **Audit append-only sin rotación** en esta versión. Si el archivo crece, se
  agrega `RotatingFileHandler` sin cambiar la API pública de `log_event`.

Ver `docs/DECISIONS.md` para la lista completa de ADRs.

## 6. Dependencias externas

Runtime (definidas en `requirements.txt` y `pyproject.toml`):

- `opencv-python ~= 4.9` — captura y rendering de video
- `mediapipe ~= 0.10` — Holistic (manos, pose, rostro)
- `numpy < 2` — operaciones vectoriales
- `tensorflow ~= 2.15` — Keras LSTM
- `scikit-learn ~= 1.4` — split + métricas
- `pillow ~= 10.0` — generación y lectura de GIF
- `bcrypt ~= 4.1` — hashing de passwords

## 7. Consideraciones de despliegue

Aplicación local; no hay despliegue remoto. La distribución es por
clonado del repositorio:

```bash
git clone <repo>
cd Lenguaje_de_senas_python
pip install -r requirements.txt
python gui_app.py
```

En Windows se recomienda abrir `abrir_app.bat`, que ejecuta `gui_app.py` con el
Python del entorno virtual. El primer arranque pide crear el profesor inicial.
