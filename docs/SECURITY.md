# Seguridad

> Versión documentada: **0.2.0**

## 1. Modelo de amenazas

La aplicación corre **localmente** en la PC del usuario. El modelo de amenazas
es acotado:

- **Activos protegidos**: el dataset de secuencias, el modelo entrenado, los
  GIFs de referencia, los hashes de password de los usuarios.
- **Atacantes considerados**: usuarios no autorizados con acceso físico al
  equipo o que comparten la instalación. Por ejemplo, un estudiante que no
  debe poder reentrenar el modelo.
- **Atacantes NO considerados**: atacantes con privilegios de OS o acceso al
  filesystem del proyecto. Si alguien puede leer/escribir libremente sobre
  `config/users.json` o sobre el código, **puede comprometer la app**. Esta
  es una limitación inherente a una aplicación local sin enclave seguro.

## 2. Autenticación

- Login obligatorio en cada arranque de `gui_app.py` o `main.py`.
- Hashes con **bcrypt** (cost factor 12).
- Validación de username: 3-30 caracteres, `[a-z0-9_]`. Case-insensitive.
- Política de password (validada al crear y al cambiar):
  - Mínimo 8 caracteres
  - Al menos un dígito
- Tras un login fallido se aplica **delay incremental** (1, 2, 4, 8, 16 segundos)
  como medida básica anti-bruteforce.

## 3. Autorización (RBAC)

- Los roles y permisos viven en `config/roles.json`.
- Cada workflow llama `requerir(permiso, rol)` al inicio. Si el rol no tiene
  el permiso, se levanta `PermissionDenied` y se vuelve al menú.
- El menú **solo muestra** opciones que el rol del usuario puede ejecutar
  (las opciones bloqueadas no aparecen).
- Defensa en profundidad: aunque alguien invoque `python -c "from workflows
  import entrenar; entrenar.main()"`, sigue requiriendo sesión activa con
  permiso `entrenar`.

## 4. Persistencia de credenciales

- `config/users.json`:
  - **No se versiona** (incluido en `.gitignore`).
  - Solo guarda hashes bcrypt, nunca passwords en texto plano.
  - Escritura atómica (escribe `users.json.tmp` y hace `replace`).
- No hay sesiones persistidas. Cerrar la app invalida la sesión.

## 5. Auditoría

Eventos registrados en `logs/audit.log`:

- Login (éxito y fallo)
- Logout
- Bootstrap del primer usuario
- Cambio de password (propio)
- Captura: inicio, fin, cancelación
- Entrenamiento: inicio, fin
- Predicción: inicio, fin, cada gesto detectado
- Gestión de usuarios: crear, eliminar, cambiar rol, resetear password

Formato de cada línea:

```
2026-05-01T15:30:00 | INFO | user=ricardo | action=login | OK
2026-05-01T15:31:12 | INFO | user=ricardo | action=train_start | OK | clases=2 muestras=60
```

## 6. Cosas que NO hace esta versión

Documentadas para que no haya falsa sensación de seguridad:

- **Encriptado de archivos**: `users.json` se guarda en JSON plano (con hashes,
  no passwords). Quien tenga acceso al filesystem puede borrarlo o reemplazarlo.
- **Bloqueo permanente** de cuentas: el delay incremental aplica solo dentro de
  la sesión de login en curso. Cerrar y reabrir resetea el contador.
- **2FA**.
- **Rotación de logs**: si `audit.log` crece, hay que rotarlo manualmente.
- **Recuperación de password**: si se pierde la única password de profesor, se
  recupera **borrando `config/users.json` y volviendo a hacer bootstrap**. Esto
  es aceptable en uso académico, no en producción.
- **Hardening del código contra deserialización**: el modelo `.h5` y las
  etiquetas `.pkl` pueden ser reemplazados externamente; cargarlos ejecuta
  código de Keras/pickle. **No cargar archivos de origen no confiable.**

## 7. Recomendaciones para administradores

- Revisar periódicamente `logs/audit.log` ante sospechas.
- Si se filtró una password, ejecutar reseteo desde un usuario con
  `gestionar_usuarios`.
- Mantener `config/users.json` fuera de cualquier backup público.
- Si el proyecto crece, evaluar migrar `users.json` a SQLite con triggers de
  auditoría más estrictos.
