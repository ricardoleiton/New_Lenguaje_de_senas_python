# Decisiones de Arquitectura (ADRs)

> Cada entrada documenta una decisión de diseño no obvia, su contexto y
> alternativas descartadas, para que se puedan revisar a futuro.

---

## ADR-001 — Estructura por dominio funcional (auth/core/vision/ml/workflows)

**Estado:** Aceptado en v0.2.0

**Contexto.** La versión inicial (v0.1.0) tenía 5 archivos `.py` en raíz que
mezclaban configuración, MediaPipe, captura, entrenamiento e inferencia. Al
sumar el sistema de roles, el archivo `utils.py` se hubiera vuelto inmanejable.

**Decisión.** Reorganizar por dominio funcional:

- `auth/` para autenticación, RBAC, sesión, audit
- `core/` para configuración y procesamiento de landmarks
- `vision/` para cámara y dibujo
- `ml/` para modelo y dataset
- `workflows/` para flujos de uso

**Alternativas descartadas.**

- Paquete instalable bajo `src/lengua_senas/`: más profesional pero invasivo
  para un proyecto académico.
- Mantener todo plano: no escalaba con el sistema de roles.

**Consecuencias.** Imports más explícitos, mejor testabilidad, sin paquete
instalable todavía. Si el proyecto crece, migrar a `src/lengua_senas/` será
un paso menor.

---

## ADR-002 — RBAC por archivo de configuración (no hardcoded)

**Estado:** Aceptado en v0.2.0

**Contexto.** El requerimiento del cliente fue "2 roles ahora, escalable a más
en el futuro". Hardcodear `if rol == "profesor"` rompe la extensibilidad.

**Decisión.** Definir roles y permisos en `config/roles.json`. El código solo
chequea permisos: `requerir("entrenar", user.rol)`.

**Alternativas descartadas.**

- Roles enumerados como `Enum` en código: cada rol nuevo requiere edit + redeploy.
- ABAC (atributos): overkill para una app local con 4 permisos.
- Jerarquía de roles con herencia: postergado. Si aparece el caso, se suma.

**Consecuencias.** Agregar un rol = editar JSON, sin tocar Python.

---

## ADR-003 — bcrypt cost 12 + JSON local

**Estado:** Aceptado en v0.2.0

**Contexto.** Necesitábamos persistencia de usuarios con hashes seguros. Las
alternativas eran SQLite o JSON.

**Decisión.** JSON local con hashes bcrypt cost 12.

**Razones.**

- 2 roles + decenas de usuarios no justifican SQLite.
- bcrypt cost 12 ≈ 250 ms por verify en CPU 2026: aceptable para una sesión
  interactiva, prohibitivo para fuerza bruta.
- JSON es human-readable: facilita auditoría y debugging.

**Cuándo migrar a SQLite.** Si el proyecto necesita: auditoría más fina,
multi-tenant, queries complejas, o si users.json supera ~1000 entradas.

---

## ADR-004 — Sesión solo en memoria (no persistencia de tokens)

**Estado:** Aceptado en v0.2.0

**Contexto.** Hay dos formas de manejar sesión en una app local: persistirla
(token en archivo) o requerir login en cada arranque.

**Decisión.** Sin persistencia. Cada arranque de `gui_app.py` o `main.py`
requiere login.

**Razones.**

- App local de uso académico: re-loguearse no es disruptivo.
- Sin tokens persistidos no hay superficie de robo de tokens.
- Cierra automáticamente el riesgo de "computadora compartida sin logout".

---

## ADR-005 — Audit log append-only sin rotación

**Estado:** Aceptado en v0.2.0

**Contexto.** Auditoría requerida por el requerimiento del cliente.

**Decisión.** `logs/audit.log` con `FileHandler` simple, sin rotación.

**Razones.**

- Volumen esperado bajo: ~10-100 eventos por día por usuario.
- Sin rotación = sin riesgo de perder evidencia por config mal seteada.
- Si crece, sumar `RotatingFileHandler` es un cambio interno (la API
  pública `log_event` no cambia).

---

## ADR-006 — Defense in depth: chequeo de permiso en menú **y** en workflow

**Estado:** Aceptado en v0.2.0

**Contexto.** El menú podría ser la única barrera (al filtrar opciones según
rol). Pero un usuario podría importar un workflow directamente.

**Decisión.** Doble chequeo:

1. El menú filtra opciones visibles según permisos.
2. Cada workflow llama `requerir(permiso, rol)` al inicio de su `main()`.

**Razones.** Costo marginal (una línea por workflow), beneficio claro.

---

## ADR-007 — Versionado siguiendo SemVer + archivo `version.py`

**Estado:** Aceptado en v0.2.0

**Contexto.** El cliente pidió poder hacer seguimiento de versiones.

**Decisión.**

- SemVer (`MAJOR.MINOR.PATCH`).
- Fuente única de verdad: `version.py` con `__version__ = "0.2.0"`.
- `pyproject.toml` mantiene la misma versión.
- v0.1.0 = "Holistic Unificado" (commit inicial).
- v0.2.0 = sumó RBAC, login, audit, reorganización en módulos.
- Cada versión documentada en `docs/CHANGELOG.md`.

**Bumps esperados.**

- PATCH: bugfix sin cambio funcional.
- MINOR: nuevas funcionalidades retrocompatibles.
- MAJOR: cambio incompatible (ej. cambio de schema de `users.json`).

---

## ADR-008 — Bootstrap interactivo del primer profesor

**Estado:** Aceptado en v0.2.0

**Contexto.** ¿Cómo crear el primer usuario cuando no hay nadie?

**Decisión.** Wizard interactivo en `main.py`: si `config/users.json` no existe,
pedir al usuario que cree un profesor inicial.

**Alternativas descartadas.**

- Script `init.py` separado: agrega un paso extra para arrancar.
- Usuario `admin/admin123` precargado: inseguro si se olvida cambiar.

**Consecuencias.** Bajar la app, ejecutarla, crear profesor. Una sola pasada.
