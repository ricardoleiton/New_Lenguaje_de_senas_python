# Relevamiento técnico — Lenguaje_de_senas_python

> Documento de relevamiento técnico únicamente. **No se modificó código.**
> Confianza por hallazgo: `CERTEZA` (verificado en código), `ALTA`, `MEDIA`,
> `INFERIDA` (baja certeza), `NO DETERMINADO` cuando no hay evidencia suficiente.
> Fecha: 2026-05-01.
>
> **Nota:** este documento es histórico. Describe el estado inicial relevado y
> puede mencionar datos ya superados por la evolución del proyecto: GUI,
> selección de cámara, captura 10×10, palabras completas y modelo reentrenado.

## 0. Metodología

- Lectura completa de los 5 `.py` del proyecto.
- Inspección programática de `requirements.txt`, `README.md`, secuencias `.npy`,
  `models/modelo_lstm.h5` (vía `h5py`) y `models/etiquetas.pkl` (vía `pickle`).
- Inspección de árbol de carpetas y tamaños.
- Sin ejecución de captura/entrenamiento/predicción.

## 1. Resumen ejecutivo `CERTEZA`

MVP funcional de reconocimiento de Lengua de Señas en ~280 LOC Python distribuidas
en 5 módulos (`main.py`, `utils.py`, `capturar_secuencias.py`, `entrenar_modelo.py`,
`predecir_secuencias.py`). Stack: **MediaPipe Holistic** para extracción de
landmarks (147 features/frame: 2 manos + 2 hombros + 5 puntos faciales) +
**LSTM Keras** sobre secuencias de 30 frames + **OpenCV** para captura/visualización
+ **PIL** para GIFs de referencia.

Estado real: **2 clases entrenadas** (`a`, `trabajar`) pese a que el README anuncia
a-z, 0-9, palabras y frases. No hay bugs bloqueantes, pero sí riesgos: borrado
destructivo de datos al recapturar, sin pin de versiones, sin holdout test, sin
tests automáticos, normalización global cuestionable, captura sin timeout.

## 2. Descripción real del sistema `CERTEZA`

App de escritorio CLI: webcam → MediaPipe Holistic → vector 147 floats/frame
→ LSTM clasifica gesto sobre ventana de 30 frames → muestra etiqueta y GIF de
referencia. Interacción por `input()` y ventanas OpenCV. No hay servidor, no hay
API, no hay UI gráfica. Persistencia local en `data/`, `gifs/`, `models/`.

## 3. Estructura del proyecto `CERTEZA`

```
Lenguaje_de_senas_python/
├── README.md                  3994 B
├── requirements.txt             65 B
├── main.py                    1099 B   Menú CLI (4 opciones)
├── utils.py                   4731 B   Config + helpers MediaPipe
├── capturar_secuencias.py     6229 B   Captura webcam -> .npy + .gif
├── entrenar_modelo.py         3039 B   LSTM Keras (Sequential)
├── predecir_secuencias.py     4136 B   Inferencia en vivo
├── data/secuencias/
│   ├── a/         a_0..a_29.npy           30 archivos
│   └── trabajar/  trabajar_0..29.npy       30 archivos
├── gifs/
│   ├── a.gif         1.81 MB
│   └── trabajar.gif  1.53 MB
└── models/
    ├── modelo_lstm.h5     862 KB
    └── etiquetas.pkl       31 B   ['a', 'trabajar']
```

Cada `.npy` tiene shape `(30, 147)` dtype `float64` (verificado).
Único commit en git: `4b4f545 Versión Unificado con Holistic`. Branch `main`,
remoto `origin`.

## 4. Flujo funcional `CERTEZA`

```
[Usuario]
   │
   ▼
main.py (menú 1-4)
   ├── 1 → capturar_secuencias.main()
   │        ├─ input(clase)
   │        ├─ BORRA secuencias previas SIN CONFIRMACIÓN  ⚠ R1
   │        ├─ Webcam(1280×720) + Holistic
   │        ├─ Loop 30 secuencias × 30 frames
   │        │    └─ extract_holistic_landmarks → normalize → validate
   │        ├─ np.save(.npy)
   │        └─ generar_gif(primera muestra)
   │
   ├── 2 → entrenar_modelo.main()
   │        ├─ cargar_datos() recorre data/secuencias/*
   │        ├─ train_test_split 80/20 (sin stratify, sin holdout)
   │        ├─ Sequential: LSTM(64,rs)→BN→LSTM(32)→Drop(.3)→Dense(64,relu)→Dense(N,softmax)
   │        ├─ Adam + sparse_categorical_crossentropy + accuracy
   │        ├─ fit(epochs=100, batch=16, callbacks=[EarlyStop,ReduceLR])
   │        ├─ save modelo_lstm.h5
   │        └─ pickle etiquetas.pkl
   │
   └── 3 → predecir_secuencias.main()
            ├─ load_model + load etiquetas
            ├─ Webcam + Holistic
            ├─ buffer deque(maxlen=30) → al llenar:
            │    ├─ predict → idx, confianza
            │    ├─ pred_buffer deque(maxlen=3) consenso 2/3
            │    └─ if conf>0.6 → mostrar texto + GIF
            └─ buffer.clear()  (NO ventana deslizante)
```

## 5. Componentes principales `CERTEZA`

| Componente | Archivo | Responsabilidad |
|---|---|---|
| Menú CLI | `main.py` | Routing entre los 3 flujos |
| Configuración | `utils.Config` | Rutas, shapes, hiperparámetros MediaPipe |
| Featurization | `utils.extract_holistic_landmarks` + `normalize_landmarks` + `validate_landmarks` | Contrato 147 floats/frame |
| Captura | `capturar_secuencias` | Webcam → `.npy` + `.gif` |
| Modelo | `entrenar_modelo.construir_modelo` | LSTM apilado |
| Inferencia | `predecir_secuencias` | Loop tiempo real + UX OpenCV |

## 6. Dependencias `CERTEZA`

Declaradas en `requirements.txt` sin pin de versiones:
- `opencv-python` — `cv2.VideoCapture`, `imshow`, `putText`, `flip`, conversión de color
- `mediapipe` — `solutions.holistic.Holistic`, `drawing_utils`, `FACEMESH_TESSELATION`,
  `HAND_CONNECTIONS`, `POSE_CONNECTIONS`
- `numpy` — arrays, `np.save`, `np.load`, `argmax`
- `tensorflow` (Keras) — `Sequential`, `LSTM`, `BatchNormalization`, `Dropout`,
  `Dense`, `EarlyStopping`, `ReduceLROnPlateau`, `load_model`
- `scikit-learn` — `train_test_split`
- `pillow` — `Image.open/save` para GIFs

Stdlib: `os`, `sys`, `time`, `pickle`, `collections.deque/Counter`, `platform`.

**Riesgo:** Sin pin → `tensorflow` y `mediapipe` cambian API entre minor versions.

## 7. Modelo de datos / archivos generados `CERTEZA`

- **Dato crudo:** no se persiste video, solo landmarks normalizados.
- **Dato procesado:** `data/secuencias/<clase>/<clase>_<i>.npy`,
  `np.ndarray(30, 147) float64`. ~35 KB por archivo.
- **GIF:** `gifs/<clase>.gif`, 300×300, 30 frames, duration=100 ms,
  generado solo de la primera muestra.
- **Modelo:** `models/modelo_lstm.h5` formato Keras H5 legacy.
  Verificado: `LSTM(64) → BN → LSTM(32) → Dropout(0.3) → Dense(64) → Dense(2)`.
  Optimizer Adam con `learning_rate≈6.25e-5` (lr inicial reducido por callback).
- **Etiquetas:** `models/etiquetas.pkl` = lista Python `['a', 'trabajar']`.

Sin esquema de versionado (no DVC, no MLflow, no nombres con timestamp).
Sin metadatos por captura (autor, fecha, condiciones).

## 8. Riesgos técnicos

| # | Riesgo | Sev | Evidencia |
|---|---|---|---|
| R1 | Borrado destructivo previo a captura | **A** | `capturar_secuencias.py` L103-106 |
| R2 | Mismatch README ↔ modelo entrenado | **A** | `etiquetas.pkl` vs `README.md` L11-14 |
| R3 | Sin pin de versiones | **A** | `requirements.txt` |
| R4 | Sin test holdout ni `stratify=y` | **M** | `entrenar_modelo.py` L48 |
| R5 | Sin reproducibilidad TF/NumPy | **M** | falta `tf.random.set_seed` |
| R6 | Captura puede colgar (sin timeout) | **M** | `capturar_secuencias.py` L62-89 |
| R7 | Normalización global mezcla manos+pose+rostro | **M** | `utils.normalize_landmarks` |
| R8 | `predecir_secuencias` no chequea modelo existente | **M** | falta guard antes de `load_model` |
| R9 | `pickle` de etiquetas (deserialización insegura) | **B** | `entrenar_modelo.py` L65 |
| R10 | GIFs con personas versionados en git, sin política PII/consentimiento | **M** | `gifs/*.gif` |
| R11 | 30 muestras × 1 señante por clase (probable) | **M** | inferido del flujo |

## 9. Deuda técnica `CERTEZA`

- Sin `LICENSE` (README declara MIT, archivo ausente).
- Sin `.gitignore` visible.
- Sin `pyproject.toml` ni lockfile.
- Sin tests (cero `test_*.py`).
- Sin type hints. Docstrings parciales.
- `utils.print_system_info()` definido y **nunca llamado**.
- `import mediapipe as mp` dentro de función (`capturar_secuencias.draw_holistic_landmarks` L17).
- `print` en lugar de `logging`.
- `.h5` legacy en lugar de `.keras` v3.
- `buffer.clear()` post-predicción descarta ventana en lugar de deslizar.
- `cv2.imshow("Ejemplo Identificado", ...)` no se cierra cuando el gesto desaparece.
- Hiperparámetros hardcodeados (`0.6`, `2/3`, `epochs=100`, `batch_size=16`) fuera de `Config`.

## 10. Recomendaciones priorizadas `INFERIDA`

### P0 — 24 a 48 h, sin riesgo
1. Reemplazar el borrado destructivo en `capturar_secuencias.py` L103-106 por
   confirmación explícita o sufijo timestamp.
2. Agregar guard `os.path.exists(Config.MODEL_PATH)` + mensaje guía al inicio
   de `predecir_secuencias.main()`.
3. Pin de versiones en `requirements.txt` (al menos `tensorflow~=2.15`,
   `mediapipe~=0.10`, `opencv-python~=4.9`, `numpy<2`).
4. Agregar `.gitignore` (incluir `__pycache__/`, `*.pyc`, secuencias/modelos
   experimentales).
5. Sincronizar README con el alcance real (2 clases) o entrenar más antes de
   publicar.

### P1 — 1 a 2 semanas
6. Reentrenar con `stratify=y`, holdout test 70/15/15, seeds determinísticos
   (`tf.random.set_seed`, `np.random.seed`), `ModelCheckpoint`,
   `classification_report`, matriz de confusión, persistir `history` JSON/CSV.
7. Migrar persistencia a `.keras` v3 y reemplazar `pickle` de etiquetas por `json`.
8. Tests unitarios sobre `extract_holistic_landmarks`, `normalize_landmarks`,
   `validate_landmarks` con `results` mockeados.
9. Reemplazar `print` por `logging` estructurado.
10. Captura con timeout por secuencia y modo retomable.

### P2 — 1 a 2 meses
11. Aumentar dataset: ≥3 señantes × 30 muestras × condiciones variadas, con
    consentimiento documentado.
12. Comparar normalización global vs por sub-grupo (manos / pose / rostro
    independientes).
13. Probar arquitecturas alternativas (GRU, TCN, Transformer pequeño) +
    augmentations temporales (time warp, dropout temporal).
14. Empaquetar como `pyproject.toml` con entry-point `lengua-senas`.
15. Inferencia con ventana deslizante (stride configurable) para reducir latencia.

## 11. Documentación faltante `CERTEZA`

- `LICENSE` (MIT prometida en README).
- `CHANGELOG.md`.
- `CONTRIBUTING.md` (cómo agregar nuevas clases).
- `docs/`:
  - Diagrama de pipeline (captura → train → predict).
  - **Spec del contrato de 147 features**: orden exacto, índices MediaPipe,
    qué se hace con manos faltantes (zeros).
  - Política de datos: consentimiento de señantes, retención, anonimización.
  - Troubleshooting cámara/MediaPipe/TF GPU/CPU.
  - Reporte de métricas por clase, baseline, condiciones de evaluación.

## 12. Próximos pasos sugeridos

- Definir si el objetivo es **académico** (entrega de cátedra) o **producto**.
- Si académico → P0 + sincronizar README + 1 reporte de métricas + 1 página
  de arquitectura.
- Si producto → P0+P1, gobierno de dataset, packaging, evaluar migración
  parcial (ver §13).

## 13. Python vs migración `INFERIDA`

**Mantener Python para entrenar y experimentar.** El stack
(MediaPipe + TF/Keras + OpenCV) es nativo Python; cualquier alternativa pierde
productividad sin ganancia clara para 2-50 clases offline. El cuello de botella
real hoy es el **dataset**, no el lenguaje.

**Considerar migración parcial solo si hay driver concreto:**
- Distribuir como app de escritorio para usuario final no técnico → empaquetar
  Python (PyInstaller/Briefcase) es viable pero pesado. Alternativa: exportar
  a **TFLite/ONNX** y embebernlo en **Electron/Tauri** o **MAUI/Avalonia**.
- Tiempo real en web/móvil → **MediaPipe Tasks for Web** + LSTM exportado a
  **TFJS** corre en navegador sin servidor.
- Producción multi-tenant con SLA → ONNX + `onnxruntime` o NVIDIA Triton.

**Lo que no recomiendo:** reescribir captura+train+predict en otro lenguaje
"porque sí". TF/Keras+MediaPipe en Python es el camino menos costoso para
iterar el modelo.

## 14. Huecos y archivos que pediría

- Confirmación del **objetivo del proyecto** (académico vs producto vs demo).
- Cantidad de señantes que participaron en la captura actual.
- Si hay un dataset pendiente de incorporar (videos, otros corpora) que no
  esté en este repo.
- Resultado real del último entrenamiento (loss, accuracy por clase).
  No hay log persistido en el repo.
- Restricciones (target hardware, latencia objetivo, idioma de señas — LSA / ASL / otro).
