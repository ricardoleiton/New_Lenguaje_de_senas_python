# Roles y permisos

> Versión documentada: **0.2.0**
> Última actualización: 2026-06-03

## 1. Roles incluidos

| Rol         | Descripción                                              |
|-------------|----------------------------------------------------------|
| estudiante  | Solo uso de la predicción en tiempo real                 |
| profesor    | Acceso completo: capturar, entrenar, predecir, gestionar usuarios |

## 2. Permisos disponibles

| Permiso              | Habilita                                          |
|----------------------|---------------------------------------------------|
| `predecir`           | Workflow de predicción en vivo                    |
| `capturar`           | Grabar letras, números o palabras para el dataset |
| `entrenar`           | Reentrenar el modelo LSTM y activar versiones entrenadas |
| `gestionar_usuarios` | Submenú de alta/baja/edición de usuarios          |

## 3. Cómo agregar un rol nuevo (sin tocar código)

Editá `config/roles.json` y agregá una entrada bajo `roles`:

```json
{
  "permisos_disponibles": ["capturar", "entrenar", "predecir", "gestionar_usuarios"],
  "roles": {
    "estudiante": {
      "descripcion": "Solo uso de la predicción",
      "permisos": ["predecir"]
    },
    "profesor": {
      "descripcion": "Acceso completo",
      "permisos": ["capturar", "entrenar", "predecir", "gestionar_usuarios"]
    },
    "asistente": {
      "descripcion": "Captura y predicción, sin entrenamiento ni gestión",
      "permisos": ["capturar", "predecir"]
    }
  }
}
```

Reinicia la app y el rol queda disponible. El submenú "Gestionar usuarios" del
profesor ya lo va a listar.

## 4. Cómo agregar un permiso nuevo

Más invasivo: requiere tocar el código del workflow al que ese permiso protege.

1. Sumar el permiso al array `permisos_disponibles` en `roles.json`.
2. Asignar el permiso a los roles que correspondan.
3. En el workflow protegido, llamar:
   ```python
   from auth import requerir, usuario_actual
   requerir("mi_nuevo_permiso", usuario_actual().rol)
   ```
4. Si el workflow se invoca desde el menú principal, sumarlo a `WORKFLOWS` en
   `main.py`.

## 5. Cómo cambiar el rol de un usuario

Desde la app gráfica, logueado como profesor:

1. Panel principal → "Gestionar usuarios"
2. Seleccionar usuario en la tabla.
3. Elegir nuevo rol.
4. Presionar "Cambiar rol".

Equivale a editar `config/users.json` directamente, pero la app valida que el
rol exista en `roles.json` y deja registro en `audit.log`.

## 6. Política de "least privilege"

- Cuando se crea un usuario nuevo desde la gestión, el rol se elige
  explícitamente. **No hay default a "profesor"**.
- El bootstrap inicial es la única excepción: el primer usuario se crea como
  `profesor` para tener un punto de partida administrable.
- Recomendación: dar `profesor` solo a quienes realmente entrenen el modelo.
  El resto debería ser `estudiante`.
