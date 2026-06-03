# Troubleshooting

> Versión documentada: **0.2.0**

## Cámara

### "No se abre la ventana de captura"

- Verificar que ninguna otra app esté usando la cámara.
- Desde la GUI o CLI usar **Seleccionar cámara** para probar otro dispositivo.
- Como último recurso, editar `core/config.py` → `CAMERA_INDEX = 1` (o 2, etc.).
- En Linux verificar permisos de `/dev/video0`.

### "MediaPipe no detecta mis manos"

- Iluminación pobre o fondo muy ruidoso → mejorar iluminación.
- Distancia muy lejana → acercarse a 60-100 cm de la cámara.
- Bajar `DETECTION_CONFIDENCE` y `TRACKING_CONFIDENCE` en `core/config.py`
  (por ejemplo a 0.5 y 0.3 respectivamente).

### "Captura se cuelga, no avanza el contador de frames"

A partir de v0.2.0 la captura tiene **timeout** (`CAPTURE_TIMEOUT_SECONDS`,
default 15s por secuencia). Si saltea con timeout, mejorar visibilidad y
reintentar la captura.

## Login

### "Olvidé la única password de profesor"

Aplicación local sin recuperación automática. Para resetear:

1. Cerrar la aplicación.
2. Borrar `config/users.json`.
3. Ejecutar `python gui_app.py` o `abrir_app.bat` — el bootstrap te pedirá crear un
   nuevo profesor.

**Atención:** esto no recupera al usuario anterior, lo reemplaza.

### "Después de N intentos fallidos no me deja"

Es la medida anti-bruteforce. El delay incremental llega hasta 16 segundos
entre intentos. **Cerrar y reabrir la app resetea el contador.**

### "El audit log no se está escribiendo"

- Verificar que existe la carpeta `logs/`. Si no, créala manualmente
  (`mkdir logs`).
- Verificar permisos de escritura.

## Entrenamiento

### `❌ No se encontraron clases en data/secuencias/`

No hay datos para entrenar. Capturá al menos 1 clase con la opción
"Capturar letra, número o palabra".

### `❌ Se necesitan al menos 2 clases con datos para entrenar`

El modelo es multi-clase y no tiene sentido entrenar con una sola. Capturá
al menos 2 clases distintas antes de entrenar.

### `⚠ Pocas muestras para holdout test. Usando split 80/20 sin test.`

El dataset es muy chico para hacer 70/15/15. Se entrena con 80/20 sin test.
Para tener métricas en holdout test, capturá más muestras por clase.

### "El entrenamiento se queda sin avanzar (early stopping)"

`EarlyStopping` corta cuando la `val_loss` no mejora durante 10 epochs. Es
esperable y deseable. El modelo se restaura a los mejores pesos.

## Predicción

### `❌ No se encontró el modelo en models/modelo_lstm.h5`

No hay modelo entrenado. Si sos profesor, ejecutá la opción "Entrenar modelo
LSTM". Si sos estudiante, pedile a un profesor que entrene primero.

### "La predicción es muy errática / cambia constantemente de gesto"

- Aumentá `PREDICTION_CONFIDENCE_THRESHOLD` (default 0.6) en `core/config.py`.
- Aumentá `PREDICTION_CONSENSUS` (default 2 de 3) para exigir más consistencia.
- Verificá que el dataset de entrenamiento tenga muestras variadas.

### "El panel de referencia queda vacío"

Es normal mientras no haya una detección estable. La predicción abre siempre
dos ventanas: cámara y referencia. La referencia se completa con el GIF guardado
cuando se identifica una letra, número o palabra.

## Dependencias

### `ImportError: No module named 'bcrypt'`

Falta instalar la dependencia. Desde la raíz del proyecto:

```bash
pip install -r requirements.txt
```

### `bcrypt` falla al instalar en Windows

> **Caso confirmado en Windows (2026-05-01):** la instalación estándar
> de bcrypt puede fallar si Python intenta compilarlo desde fuente y el
> sistema no tiene las herramientas C necesarias.

**Solución verificada en Windows:**

```powershell
pip install --only-binary :all: "bcrypt~=4.1"
```

El flag `--only-binary :all:` fuerza a `pip` a instalar la wheel
precompilada (binaria) en lugar de compilar desde código fuente. Es la
manera recomendada de instalar bcrypt en Windows cuando no hay
Microsoft Visual C++ Build Tools instaladas.

Después de este comando, `python gui_app.py` y `python main.py` arrancan sin
problemas.

**Linux/macOS:** generalmente alcanza con `pip install -r requirements.txt`
porque las wheels precompiladas están disponibles para distribuciones comunes.

### `tensorflow` no encuentra GPU

Esperable. La app funciona en CPU sin cambios. Para GPU, instalar las
versiones compatibles de TF y los drivers CUDA (consultar la doc oficial
de TensorFlow).

### MediaPipe falla al inicializar Holistic

- Confirmar que estás en Python 3.10 o 3.11.
- Reinstalar: `pip install --force-reinstall mediapipe`.
- En Linux puede faltar `libGL`: `sudo apt-get install libgl1`.

## Logs útiles

- `logs/audit.log` — quién hizo qué y cuándo.
- `models/history.json` — historia de loss/accuracy del último entrenamiento.
- `models/latest_model_version.json` — metadata de la última versión entrenada.
- `models/versions/<timestamp>/metadata.json` — detalle histórico de una corrida.

Si nada de lo de arriba ayuda, abrir un issue con: SO, versión de Python,
versión de la app (`__version__` en `version.py`), traza completa del error.
