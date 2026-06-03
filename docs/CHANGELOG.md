# Changelog

Todas las versiones notables del proyecto, en formato [Keep a Changelog](https://keepachangelog.com/es/1.1.0/)
y siguiendo [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Añadido
- Interfaz gráfica de escritorio (`gui_app.py`) con login, panel por rol,
  captura, entrenamiento, predicción, gestión de usuarios y cambio de contraseña.
- Launcher Windows `abrir_app.bat` para abrir la GUI sin usar PowerShell/CMD.
- Selector de cámara en GUI y CLI para equipos con más de una webcam.
- Captura de palabras completas además de letras y números.
- Resumen de letras, números y palabras ya capturados antes de capturar.
- Cuenta regresiva inicial de 5 segundos antes de empezar el bloque de captura.
- Predicción con dos ventanas: cámara en vivo y panel de referencia guardada.
- Suite inicial de tests automatizados con `unittest`.
- Documento `docs/TESTING.md` con alcance, ejecución y próximos tests sugeridos.
- Paquete `gui/` para separar la interfaz Tkinter por aplicación, tema, salida
  y pantallas.
- Paquete `services/` para separar servicios de captura, entrenamiento y
  predicción de la capa de workflows.

### Cambiado
- Captura reducida a 10 secuencias por clase y 10 frames por secuencia.
- El loader del dataset remuestrea secuencias antiguas a 10 frames al entrenar.
- El modelo actual fue reentrenado con clases `1`, `2`, `a`, `b`, `c`, `d`,
  `hola`, `trabajar`.
- `gui_app.py` quedó como entrada liviana compatible con el launcher existente.
- Workflows de captura, entrenamiento y predicción reducidos a sesión, permisos
  y delegación a servicios.
- README y documentación actualizados para reflejar el flujo con GUI.

### Documentación
- Caso confirmado de instalación en Windows: `bcrypt` requiere instalación
  binaria con `pip install --only-binary :all: "bcrypt~=4.1"` cuando el
  sistema no tiene Microsoft Visual C++ Build Tools.
- Detalle agregado en `README.md` (sección Instalación → Nota para Windows)
  y en `docs/TROUBLESHOOTING.md` (sección Dependencias).

---

## [0.2.0] — 2026-05-01

### Añadido

- Sistema de **roles y permisos (RBAC)** con archivo de configuración
  `config/roles.json`. Roles iniciales: `estudiante`, `profesor`.
- **Login obligatorio** con username + password (hashing bcrypt cost 12).
- **Wizard de bootstrap** para crear el primer profesor cuando no hay usuarios.
- **Submenú de gestión de usuarios** (visible solo para roles con
  `gestionar_usuarios`): listar, crear, eliminar, cambiar rol, resetear password.
- **Cambio de password propio** desde el menú (todos los usuarios).
- **Audit log** en `logs/audit.log` con login/logout, captura, entrenamiento,
  predicción de gestos y operaciones de usuarios.
- **Anti-bruteforce básico**: delay incremental (1, 2, 4, 8, 16s) tras login fallido.
- **Reorganización del proyecto** por dominio funcional:
  `auth/`, `core/`, `vision/`, `ml/`, `workflows/`, `docs/`.
- **Documentación técnica** en `docs/`: ARCHITECTURE, SECURITY, ROLES,
  TROUBLESHOOTING, DECISIONS, CHANGELOG, DEVELOPMENT.
- `pyproject.toml`, `LICENSE` (MIT), `.gitignore`, `version.py`.
- Versionado central en `version.py` con `__version__`, `__app_name__`,
  `__release_date__`.

### Cambiado

- **`requirements.txt`** ahora tiene versiones pineadas (TF 2.15, MediaPipe 0.10, etc.).
- **Captura**: confirmación explícita antes de borrado destructivo de secuencias
  previas (mitiga R1 del relevamiento técnico).
- **Captura**: timeout por secuencia (`CAPTURE_TIMEOUT_SECONDS`, default 15s)
  para evitar cuelgue infinito si MediaPipe no detecta nada.
- **Entrenamiento**:
  - Split estratificado 70/15/15 (con fallback a 80/20 si hay pocas muestras).
  - Seeds determinísticos (`np.random.seed`, `tf.random.set_seed`).
  - `ModelCheckpoint` para no perder progreso ante crash.
  - `classification_report` y matriz de confusión post-entrenamiento.
  - Persistencia de `history.json`.
- **Predicción**:
  - Guard de existencia de modelo y etiquetas.
  - Cierre de la ventana del GIF al expirar el gesto.
  - Reset del buffer de predicciones al cambiar de gesto.
  - Thresholds movidos a `core/config.py`.
- **`Config`** migrada a `@dataclass(frozen=True)` (inmutable).

### Eliminado

- Archivos viejos: `utils.py`, `capturar_secuencias.py`, `entrenar_modelo.py`,
  `predecir_secuencias.py`. Su contenido fue reorganizado en los módulos
  nuevos.

### Seguridad

- Hashes bcrypt (sin passwords en texto plano).
- `config/users.json` excluido de git.
- Doble chequeo de permisos: en menú (filtrado) y en workflow (defense in depth).

---

## [0.1.0] — 2026-05-01 (commit inicial)

Versión "Holistic Unificada", commit `4b4f545`.

### Funcionalidad inicial

- Captura de secuencias con MediaPipe Holistic (147 features por frame).
- Entrenamiento LSTM Keras (LSTM 64 → BN → LSTM 32 → Dropout 0.3 → Dense 64 → Dense N).
- Predicción en tiempo real con buffer de 30 frames.
- Generación automática de GIF de referencia por clase.
- Menú CLI con 4 opciones (capturar, entrenar, predecir, salir).

### Datasets entregados

- 2 clases entrenadas: `a` (letra) y `trabajar` (palabra).
- 30 secuencias × 30 frames × 147 features por clase.

---

## Convención de bumps

- **PATCH** (`0.2.X`): bugfix sin cambio funcional.
- **MINOR** (`0.X.0`): nueva funcionalidad retrocompatible.
- **MAJOR** (`X.0.0`): cambio incompatible (ej. cambio de schema de
  `users.json`, breaking en API de `requerir`, etc.).
