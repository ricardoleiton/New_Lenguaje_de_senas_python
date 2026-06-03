# Levantamiento de necesidades

> Proyecto: Lengua de Señas - Holistic Unificado  
> Autor: Ricardo Leitón  
> Versión documentada: 0.2.0  
> Fecha de actualización: 2026-06-02

## 1. Necesidad del usuario

El usuario necesita una herramienta local que permita reconocer gestos de lengua de señas mediante una cámara web, orientada inicialmente a letras, números y palabras completas. La herramienta debe ser usable por personas con distinto nivel técnico, por lo que no debe depender exclusivamente de PowerShell o CMD para su operación cotidiana.

La necesidad principal es facilitar la captura, entrenamiento y predicción de gestos desde una interfaz simple, con roles diferenciados para quienes administran el sistema y quienes solo realizan predicciones.

Necesidades identificadas:

- Capturar nuevas clases de señas de manera guiada.
- Entrenar un modelo con los datos capturados localmente.
- Predecir gestos en tiempo real usando cámara web.
- Mostrar una referencia visual guardada cuando se detecta una clase.
- Permitir uso en equipos con una o más cámaras.
- Evitar que usuarios sin autorización modifiquen datos o reentrenen el modelo.
- Mantener registro de acciones relevantes.

## 2. Problema a resolver

El problema central es la ausencia de una aplicación local, sencilla y controlada para reconocer gestos de lengua de señas a partir de video en tiempo real.

Sin una herramienta específica, el proceso queda fragmentado:

- La captura de datos puede ser inconsistente.
- El entrenamiento puede depender de scripts técnicos.
- La predicción puede requerir conocimientos de consola.
- No hay separación clara entre usuarios que solo usan el sistema y usuarios que lo administran.
- No hay trazabilidad suficiente sobre capturas, entrenamientos o accesos.

El sistema busca resolver este problema integrando captura, entrenamiento, predicción, autenticación, roles, gestión de usuarios, selección de cámara y auditoría en una misma aplicación.

## 3. Contexto de uso

La aplicación está pensada para ejecutarse localmente en una computadora con webcam, principalmente en entornos educativos, demostrativos o de prototipado académico.

Contexto operativo:

- Uso local, sin servicios remotos.
- Ejecución recomendada desde interfaz gráfica Tkinter (`gui_app.py`) o launcher Windows (`abrir_app.bat`).
- Consola (`main.py`) disponible como alternativa de soporte.
- Cámara web como dispositivo de entrada principal.
- Datos, modelo, usuarios y logs almacenados en el filesystem del proyecto.
- Uso esperado por profesores/administradores y estudiantes/usuarios finales.

Condiciones esperadas:

- Iluminación suficiente.
- Cámara enfocando manos, rostro y hombros.
- Fondo no excesivamente ruidoso.
- Usuario ubicado a una distancia adecuada de la cámara.
- Gestos realizados de forma estable durante la captura.

## 4. Usuarios involucrados

### Profesor

Usuario administrador del sistema. Tiene acceso completo a las funciones críticas.

Responsabilidades:

- Crear y administrar usuarios.
- Capturar letras, números y palabras.
- Entrenar el modelo.
- Ejecutar predicción en tiempo real.
- Seleccionar cámara.
- Revisar resultados y repetir capturas si son deficientes.

Permisos actuales:

- `capturar`
- `entrenar`
- `predecir`
- `gestionar_usuarios`

### Estudiante

Usuario final del sistema. Su operación se limita al uso del modelo ya entrenado.

Responsabilidades:

- Seleccionar cámara si fuera necesario.
- Ejecutar predicción en tiempo real.
- Cambiar su propia contraseña.

Permisos actuales:

- `predecir`

### Administrador técnico

Rol operativo no modelado como rol separado en la app, pero presente en el ciclo de vida del proyecto.

Responsabilidades:

- Instalar Python y dependencias.
- Mantener el entorno virtual.
- Revisar errores de cámara, MediaPipe, TensorFlow u OpenCV.
- Respaldar dataset/modelos si corresponde.
- Mantener documentación y código.

## 5. Requerimientos del usuario

Los requerimientos de usuario describen necesidades desde el punto de vista de quien opera la aplicación.

| ID | Requerimiento |
|----|---------------|
| RU-01 | Como profesor, quiero iniciar sesión para acceder a funciones protegidas. |
| RU-02 | Como estudiante, quiero iniciar sesión para usar predicción sin poder modificar el sistema. |
| RU-03 | Como profesor, quiero capturar letras, números y palabras completas. |
| RU-04 | Como profesor, quiero ver qué clases ya fueron capturadas antes de capturar una nueva. |
| RU-05 | Como profesor, quiero una cuenta regresiva antes de capturar para acomodarme frente a la cámara. |
| RU-06 | Como profesor, quiero sobrescribir datos existentes solo con confirmación. |
| RU-07 | Como profesor, quiero entrenar el modelo desde la aplicación. |
| RU-08 | Como usuario, quiero seleccionar la cámara si el equipo tiene más de una. |
| RU-09 | Como usuario, quiero ejecutar predicción en tiempo real desde una interfaz gráfica. |
| RU-10 | Como usuario, quiero ver la cámara y la referencia guardada en ventanas separadas y ordenadas. |
| RU-11 | Como usuario, quiero que la predicción muestre la clase detectada y su confianza. |
| RU-12 | Como profesor, quiero gestionar usuarios, roles y contraseñas. |
| RU-13 | Como usuario, quiero cambiar mi propia contraseña. |
| RU-14 | Como responsable del sistema, quiero que las acciones relevantes queden registradas. |
| RU-15 | Como usuario no técnico, quiero abrir la aplicación sin escribir comandos. |

## 6. Requerimientos del sistema

Los requerimientos del sistema describen capacidades técnicas necesarias para satisfacer los requerimientos de usuario.

| ID | Requerimiento |
|----|---------------|
| RS-01 | El sistema debe ejecutarse localmente en Python 3.10 o superior. |
| RS-02 | El sistema debe proveer una GUI de escritorio con Tkinter. |
| RS-03 | El sistema debe conservar una alternativa CLI para soporte. |
| RS-04 | El sistema debe capturar video desde cámara web mediante OpenCV. |
| RS-05 | El sistema debe detectar landmarks con MediaPipe Holistic. |
| RS-06 | El sistema debe extraer 147 features por frame. |
| RS-07 | El sistema debe capturar 10 frames por secuencia. |
| RS-08 | El sistema debe capturar 10 secuencias por clase. |
| RS-09 | El sistema debe guardar secuencias en `data/secuencias/<clase>/`. |
| RS-10 | El sistema debe generar un GIF de referencia por clase capturada. |
| RS-11 | El sistema debe entrenar un modelo LSTM con TensorFlow/Keras. |
| RS-12 | El sistema debe guardar modelo, etiquetas e historia de entrenamiento. |
| RS-13 | El sistema debe cargar el modelo entrenado para predicción. |
| RS-14 | El sistema debe validar incompatibilidades entre frames configurados y modelo entrenado. |
| RS-15 | El sistema debe implementar autenticación con usuarios locales. |
| RS-16 | El sistema debe guardar contraseñas con bcrypt, nunca en texto plano. |
| RS-17 | El sistema debe aplicar RBAC según `config/roles.json`. |
| RS-18 | El sistema debe registrar eventos auditables en `logs/audit.log`. |
| RS-19 | El sistema debe permitir descubrir y seleccionar cámaras disponibles. |
| RS-20 | El sistema debe funcionar sin conexión a internet durante el uso normal. |

## 7. Alcance funcional

### Incluido

El alcance actual incluye:

- Interfaz gráfica de escritorio.
- Login y bootstrap del primer profesor.
- Roles `profesor` y `estudiante`.
- Gestión de usuarios por profesor.
- Cambio de contraseña propia.
- Captura de letras, números y palabras completas.
- Resumen de clases ya capturadas.
- Cuenta regresiva inicial antes de capturar.
- Captura de 10 secuencias por clase, 10 frames por secuencia.
- Generación de GIF de referencia.
- Entrenamiento del modelo LSTM.
- Predicción en tiempo real.
- Doble ventana en predicción: cámara y referencia.
- Selección de cámara.
- Auditoría local.
- Documentación técnica.

### No incluido actualmente

Queda fuera del alcance actual:

- Reconocimiento gramatical de oraciones complejas.
- Concatenación automática de palabras en una oración.
- Traducción a español natural.
- Reconocimiento multiusuario robusto con dataset amplio.
- Sincronización con servicios en la nube.
- Base de datos formal; se usa JSON local.
- Empaquetado como instalador `.exe`.
- Tests automatizados completos.
- Recuperación automática de contraseña.
- Detección semántica de inicio/fin de gesto.

### Posibles ampliaciones futuras

- Modo de frase acumulada para concatenar palabras detectadas.
- Comandos gestuales como `borrar`, `espacio`, `finalizar`.
- Dataset con múltiples señantes, fondos e iluminaciones.
- Exportación de reportes de entrenamiento.
- Instalador Windows.
- Persistencia en SQLite.
- Panel de métricas para comparar versiones del modelo.

## 8. Requisitos funcionales y no funcionales

### Requisitos funcionales

| ID | Requisito funcional |
|----|---------------------|
| RF-01 | El sistema debe permitir crear el primer profesor si no existen usuarios. |
| RF-02 | El sistema debe permitir iniciar sesión con usuario y contraseña. |
| RF-03 | El sistema debe mostrar opciones según el rol del usuario. |
| RF-04 | El sistema debe permitir seleccionar cámara. |
| RF-05 | El sistema debe permitir capturar una letra. |
| RF-06 | El sistema debe permitir capturar un número. |
| RF-07 | El sistema debe permitir capturar una palabra completa. |
| RF-08 | El sistema debe listar letras, números y palabras ya capturados. |
| RF-09 | El sistema debe pedir confirmación antes de sobrescribir datos existentes. |
| RF-10 | El sistema debe mostrar cuenta regresiva antes de comenzar la captura. |
| RF-11 | El sistema debe guardar secuencias capturadas en formato `.npy`. |
| RF-12 | El sistema debe generar un GIF de referencia de la primera secuencia. |
| RF-13 | El sistema debe permitir entrenar el modelo con los datos disponibles. |
| RF-14 | El sistema debe mostrar métricas de validación y test cuando corresponda. |
| RF-15 | El sistema debe guardar `modelo_lstm.h5`, `etiquetas.pkl` y `history.json`. |
| RF-16 | El sistema debe permitir predicción en tiempo real. |
| RF-17 | El sistema debe mostrar la clase detectada y su confianza. |
| RF-18 | El sistema debe mostrar el GIF de referencia cuando exista detección. |
| RF-19 | El sistema debe permitir gestionar usuarios desde rol profesor. |
| RF-20 | El sistema debe registrar eventos de login, logout, captura, entrenamiento, predicción y gestión. |

### Requisitos no funcionales

| ID | Requisito no funcional |
|----|------------------------|
| RNF-01 | La aplicación debe ejecutarse localmente sin depender de servicios externos. |
| RNF-02 | La operación cotidiana debe poder realizarse desde GUI. |
| RNF-03 | La interfaz debe ser clara para usuarios no técnicos. |
| RNF-04 | La predicción debe responder con baja latencia, usando ventanas de 10 frames. |
| RNF-05 | El sistema debe proteger funciones críticas mediante roles. |
| RNF-06 | Las contraseñas deben almacenarse hasheadas con bcrypt. |
| RNF-07 | El sistema debe poder operar en CPU. |
| RNF-08 | El código debe mantenerse organizado por dominios funcionales. |
| RNF-09 | La configuración común debe centralizarse en `core/config.py`. |
| RNF-10 | El sistema debe proveer trazabilidad mediante audit log. |
| RNF-11 | La documentación debe mantenerse alineada con el estado actual. |
| RNF-12 | El sistema debe conservar compatibilidad con Python 3.10/3.11. |

## 9. Diseño técnico

### Arquitectura general

El sistema está organizado por dominios:

- `auth/`: autenticación, usuarios, roles, sesión y auditoría.
- `core/`: configuración, consola, UI común y procesamiento de landmarks.
- `vision/`: cámara, MediaPipe, GIFs y overlays visuales.
- `ml/`: carga de datos y arquitectura del modelo LSTM.
- `workflows/`: flujos de captura, entrenamiento, predicción y gestión.
- `gui_app.py`: entrada de arranque de la interfaz gráfica.
- `gui/`: implementación modular de la GUI por aplicación, tema, salida y pantallas.
- `services/`: servicios reutilizables para captura, entrenamiento y predicción.
- `workflows/`: orquestación con sesión, permisos y menú.
- `main.py`: alternativa de consola.

### Flujo principal

```text
Usuario → GUI/CLI → workflow → cámara/modelo/dataset → resultado visual/logs
```

### Captura

```text
selección de clase
→ selección/uso de cámara
→ confirmación con C
→ cuenta regresiva de 5 segundos
→ extracción MediaPipe Holistic
→ landmarks normalizados
→ 10 frames válidos
→ 10 secuencias por clase
→ .npy + GIF de referencia
```

Cada frame contiene 147 features:

```text
2 manos × 21 puntos × 3 coordenadas = 126
2 hombros × 3 coordenadas = 6
5 puntos faciales × 3 coordenadas = 15
Total = 147
```

### Entrenamiento

```text
data/secuencias/*
→ cargar_datos()
→ X (N, 10, 147)
→ split estratificado
→ LSTM
→ métricas
→ modelo_lstm.h5 + etiquetas.pkl + history.json
```

Arquitectura actual:

```text
LSTM(64, return_sequences)
→ BatchNormalization
→ LSTM(32)
→ Dropout(0.3)
→ Dense(64, relu)
→ Dense(N, softmax)
```

### Predicción

```text
cámara
→ MediaPipe Holistic
→ buffer de 10 frames
→ model.predict()
→ filtro por confianza
→ consenso de predicciones
→ cámara + panel de referencia
```

La predicción usa:

- `PREDICTION_CONFIDENCE_THRESHOLD = 0.6`
- `PREDICTION_HISTORY = 3`
- `PREDICTION_CONSENSUS = 2`

### Seguridad y acceso

- Usuarios en `config/users.json`.
- Passwords con bcrypt.
- Roles en `config/roles.json`.
- Sesión en memoria.
- Audit log en `logs/audit.log`.

### Datos y artefactos

- Dataset: `data/secuencias/<clase>/<clase>_<i>.npy`
- GIFs: `gifs/<clase>.gif`
- Modelo: `models/modelo_lstm.h5`
- Etiquetas: `models/etiquetas.pkl`
- Historia: `models/history.json`
- Logs: `logs/audit.log`

## 10. Desarrollo

El proyecto ya cuenta con una implementación funcional que cubre el flujo principal de captura, entrenamiento y predicción.

### Estado implementado

- GUI de escritorio.
- Launcher Windows.
- Login y roles.
- Captura de letras, números y palabras.
- Selección de cámara.
- Cuenta regresiva inicial.
- Dataset local.
- Entrenamiento LSTM.
- Predicción en tiempo real.
- Panel de referencia visual.
- Gestión de usuarios.
- Auditoría.
- Documentación técnica.

### Pendiente sugerido

- Agregar pruebas automatizadas.
- Diseñar modo de frase acumulada.
- Definir un protocolo formal de captura de dataset.
- Ampliar el dataset con más señantes y condiciones de luz/fondo.
- Evaluar reducción de features si el alcance se concentra en letras/números.
- Empaquetar como aplicación instalable.
- Agregar reportes de entrenamiento.

### Preguntas para refinar el levantamiento

1. ¿El objetivo final es reconocer solo señas aisladas o también construir oraciones completas?
2. ¿La aplicación será usada por una sola persona o por varios señantes con estilos distintos?
3. ¿El contexto principal será aula, demostración académica, atención al público u otro?
4. ¿Qué conjunto mínimo de clases debe considerarse obligatorio para la primera entrega formal?
5. ¿Las palabras completas serán gestos únicos o combinaciones de letras/palabras?
6. ¿Necesitás que el sistema genere reportes imprimibles de entrenamiento y precisión?
7. ¿Se espera distribuirlo como carpeta de proyecto o como instalador de Windows?
8. ¿Quién administrará usuarios y respaldos de dataset/modelo?
9. ¿Debe conservarse historial de modelos anteriores o alcanza con sobrescribir el modelo actual?
10. ¿La predicción debería acumular resultados en una frase visible en pantalla?
