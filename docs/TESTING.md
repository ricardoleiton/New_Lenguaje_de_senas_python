# Pruebas automatizadas

> Versión documentada: 0.2.0  
> Fecha de actualización: 2026-06-02

## Objetivo

Esta suite agrega una primera red de seguridad para las partes más sensibles del
proyecto: permisos, usuarios, dataset, landmarks y estructura de capas. Está
pensada para ejecutarse sin cámara, sin abrir ventanas y sin entrenar
TensorFlow.

Se usa `unittest`, incluido en la librería estándar de Python, para evitar sumar
dependencias nuevas.

## Cómo ejecutar

Desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

En Linux/macOS:

```bash
python -m unittest discover -s tests -v
```

## Cobertura inicial

### `tests/test_rbac.py`

Valida el sistema de roles y permisos:

- carga de roles desde un `roles.json` temporal;
- existencia de roles;
- permisos de profesor y estudiante;
- helpers `tiene_permiso` y `requerir`;
- error cuando falta el archivo de roles.

El test usa un archivo temporal para no depender del `config/roles.json` real.

### `tests/test_users.py`

Valida el módulo de usuarios:

- normalización y validación de usernames;
- política mínima de contraseña;
- creación de usuario;
- hash bcrypt en vez de password plano;
- autenticación correcta e incorrecta;
- cambio de rol;
- cambio de contraseña;
- eliminación de usuario;
- rechazo de usuario duplicado;
- rechazo de rol inexistente.

El test redirige `USERS_PATH` a un archivo temporal para no tocar
`config/users.json` real.

### `tests/test_data_io.py`

Valida carga de dataset:

- remuestreo de secuencias antiguas de 30 frames a 10 frames;
- rechazo de secuencias con cantidad incorrecta de features;
- carga de clases ordenadas alfabéticamente;
- shape final `X = (N, 10, 147)`;
- error cuando no existe el directorio de secuencias.

El test usa un directorio temporal y datos `.npy` sintéticos.

### `tests/test_landmarks.py`

Valida procesamiento de landmarks:

- salida fija de 147 features;
- relleno con ceros cuando faltan regiones;
- normalización sin `NaN`;
- rechazo de vectores vacíos, con `NaN`, con `inf` o con longitud incorrecta.

Se usan objetos falsos con la misma forma mínima que los resultados de
MediaPipe, sin inicializar MediaPipe real.

### `tests/test_gui_structure.py`

Valida la separación de la GUI:

- `gui.App` es importable desde el paquete `gui`;
- `gui_app.py` conserva el entrypoint compatible con el launcher existente.

No instancia Tkinter ni abre ventanas.

### `tests/test_services_structure.py`

Valida la separación workflow/servicio:

- existen los servicios de captura, entrenamiento y predicción;
- los workflows delegan en `services/`;
- los servicios no llaman directamente a `usuario_actual` ni a `requerir`.

Es una prueba estructural liviana para sostener la arquitectura sin cámara ni
TensorFlow real.

## Qué no cubre todavía

Esta primera suite no cubre:

- apertura real de cámara;
- ventanas OpenCV;
- flujo completo de captura con usuario frente a cámara;
- entrenamiento real del modelo;
- predicción real con modelo y cámara;
- renderizado real de pantallas Tkinter;
- auditoría sobre archivos reales;
- integración end-to-end completa.

Es intencional: esos casos son más costosos y requieren mocks o pruebas
manuales asistidas.

## Próximos tests recomendados

Prioridad sugerida:

1. Tests de `vision.camera.discover_cameras` con mock de `cv2.VideoCapture`.
2. Tests de `workflows.capturar.clases_capturadas`.
3. Tests de login/bootstrap con mocks de entrada.
4. Tests adicionales de GUI para validaciones puras, sin abrir ventanas reales.
5. Tests de entrenamiento con dataset mínimo y epochs reducidos.
6. Tests de predicción con modelo simulado.

## Criterio de aceptación actual

Antes de entregar cambios de código, ejecutar:

```powershell
.\.venv\Scripts\python.exe -m compileall -q gui_app.py main.py auth core gui ml services vision workflows tests
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

El cambio se considera aceptable si:

- la compilación termina sin errores;
- todos los tests pasan;
- no se modifica `config/users.json` real;
- no se modifica el dataset real durante los tests.
