# Guía de desarrollo

> Versión documentada: **0.2.0**

## 1. Setup local

```bash
git clone <repo>
cd Lenguaje_de_senas_python
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate           # Windows
pip install -r requirements.txt
python gui_app.py
```

En Windows también se puede abrir `abrir_app.bat`. La consola (`python main.py`)
queda como alternativa de soporte. El primer arranque pide crear el profesor
inicial.

## 2. Convenciones de código

- **Python 3.10+** (usar `tuple[...]`, `|` en types, etc.).
- Imports en este orden: stdlib, terceros, internos. Separar con líneas en blanco.
- Imports internos absolutos desde la raíz del proyecto:
  `from core.config import config`, no `from .config import config` salvo
  dentro del mismo subpaquete.
- Type hints donde sumen claridad. No es obligatorio en helpers triviales.
- Comentarios y docstrings en español (consistente con el dominio).
- `print` está OK para logs de proceso en CLI/GUI; usar `audit.log_event` para
  eventos auditables.

## 3. Convenciones de archivos / carpetas

- Cada subpaquete tiene `__init__.py` que reexporta su API pública.
- Configuración: única fuente en `core/config.py` (clase `Config`,
  instancia `config`). No agregar `os.environ` ad-hoc.
- Logs en `logs/`, datos en `data/`, modelos en `models/`. No mezclar.

## 4. Cómo agregar un workflow nuevo

1. Crear archivo en `workflows/<nombre>.py` con función `main()`.
2. Al inicio de `main()` agregar:
   ```python
   from auth import requerir, usuario_actual, log_event
   user = usuario_actual()
   if user is None:
       print("❌ No hay sesión activa")
       return
   requerir("<permiso>", user.rol)
   log_event(user.username, "<accion>_start")
   ```
3. Sumar el permiso a `config/roles.json` (en `permisos_disponibles` y en los
   roles que correspondan).
4. Registrar el workflow en `main.py`, lista `WORKFLOWS`:
   ```python
   ("Mi nueva opción", "<permiso>", "workflows.<nombre>"),
   ```
5. Si corresponde a una acción de usuario final, agregar una tarjeta/botón en
   `gui_app.py`.

## 5. Cómo subir versión

1. Editar `version.py`: bumpear `__version__` siguiendo SemVer.
2. Editar `pyproject.toml`: campo `version` igual.
3. Documentar en `docs/CHANGELOG.md`: nueva sección con fecha y cambios
   clasificados (Añadido / Cambiado / Eliminado / Seguridad).
4. Commit `chore: bump version 0.X.Y → 0.X.Z`.
5. Tag: `git tag v0.X.Z && git push --tags`.

## 6. Política de tests

Esta versión **no incluye tests automatizados** todavía (deuda técnica
documentada en el relevamiento).

Cuando se agreguen, ubicarlos en `tests/`:

```
tests/
├── test_landmarks.py
├── test_rbac.py
├── test_users.py
└── test_data_io.py
```

Recomendaciones:

- `pytest` como runner.
- Mockear `cv2.VideoCapture` y `mediapipe` (objetos pesados).
- Usar `tmp_path` para `users.json` y `roles.json` de prueba.

## 7. Sanity checks antes de commitear

```bash
# Compilar sintácticamente todos los .py
python -m compileall -q .

# Verificar imports (debe levantar SystemExit, no ImportError)
python -c "from auth import login_loop; from workflows import capturar, entrenar, predecir, gestion_usuarios"

# Lanzar GUI (ver que login/panel arrancan)
python gui_app.py

# Alternativa CLI de soporte
python main.py
```

## 8. Estructura del repositorio post-v0.2.0

Ver `docs/ARCHITECTURE.md`. Resumen:

- `auth/`, `core/`, `vision/`, `ml/`, `workflows/` → código del sistema.
- `config/` → roles.json (versionado) + users.json (gitignored).
- `data/`, `gifs/`, `models/` → datos y artefactos.
- `logs/` → audit.log (gitignored).
- `docs/` → documentación.
- `gui_app.py`, `abrir_app.bat`, `main.py`, `version.py`, `pyproject.toml`,
  `requirements.txt` → raíz.
