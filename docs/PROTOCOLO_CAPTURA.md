# Protocolo formal de captura

> Proyecto: Lengua de Señas - Holistic Unificado  
> Autor: Ricardo Leitón  
> Versión documentada: 0.2.0  
> Fecha de actualización: 2026-06-02

## 1. Objetivo

Definir un procedimiento uniforme para capturar letras, números y palabras
completas. El propósito es obtener secuencias limpias, consistentes y
comparables para entrenamiento del modelo LSTM.

## 2. Parámetros vigentes

| Parámetro | Valor |
|-----------|-------|
| Secuencias por clase | 10 |
| Frames válidos por secuencia | 10 |
| Features por frame | 147 |
| Cuenta regresiva inicial | 5 segundos |
| Timeout por secuencia | 15 segundos |
| Formato de salida | `.npy` |
| GIF de referencia | Primera secuencia válida |

## 3. Preparación del entorno

- Usar iluminación frontal o lateral suave.
- Evitar contraluz, sombras fuertes o luces intermitentes.
- Usar un fondo simple, sin movimiento detrás del usuario.
- Ubicar la cámara de forma estable.
- Verificar que manos, rostro y hombros entren en el encuadre.
- Evitar objetos que tapen manos, muñecas, rostro u hombros.
- Seleccionar la cámara correcta antes de iniciar si hay más de una.

## 4. Preparación del usuario

- Sentarse o pararse a una distancia cómoda de la cámara.
- Mantener una postura natural y repetible.
- Realizar una prueba visual antes de presionar `C`.
- Confirmar que el objetivo mostrado coincide con la letra, número o palabra a
  capturar.

## 5. Procedimiento de captura

1. Iniciar sesión con un usuario con permiso `capturar`.
2. Entrar en **Capturar gesto**.
3. Revisar las clases ya capturadas.
4. Revisar el protocolo mostrado en pantalla.
5. Seleccionar tipo: letra, número o palabra.
6. Ingresar el valor de la clase.
7. Confirmar sobrescritura solo si se desea reemplazar datos previos.
8. En la ventana de cámara, verificar el objetivo.
9. Presionar `C` para comenzar.
10. Usar la cuenta regresiva para acomodarse.
11. Mantener el gesto estable hasta completar las 10 secuencias.
12. Presionar `Q` solo si es necesario cancelar o repetir la toma.

## 6. Criterios de calidad

Una captura se considera aceptable cuando:

- la clase capturada coincide con el objetivo seleccionado;
- la mano o manos principales se ven completas;
- rostro y hombros permanecen visibles;
- el gesto se mantiene estable durante la secuencia;
- no se mezclan dos gestos en la misma secuencia;
- no aparecen objetos o personas bloqueando el gesto;
- el contador de frames avanza con la postura correcta.

## 7. Criterios para repetir captura

Repetir la toma si ocurre cualquiera de estas situaciones:

- MediaPipe pierde manos, rostro u hombros durante la toma;
- se seleccionó o realizó una clase incorrecta;
- aparece otra persona u objeto tapando el gesto;
- cambia la iluminación de forma marcada;
- el usuario se mueve fuera del encuadre;
- el contador avanza mientras el gesto todavía no está listo;
- se interrumpe la captura antes de completar las secuencias esperadas.

## 8. Nombres de clase

- Letras: una sola letra entre `A-Z`.
- Números: un solo dígito entre `0-9`.
- Palabras: texto alfabético de dos o más caracteres.
- Los espacios en palabras se normalizan como `_`.

## 9. Resultado esperado

Para cada clase se espera:

```text
data/secuencias/<clase>/<clase>_0.npy
data/secuencias/<clase>/<clase>_1.npy
...
data/secuencias/<clase>/<clase>_9.npy
gifs/<clase>.gif
```

Cada `.npy` debe tener forma:

```text
(10, 147)
```

## 10. Recomendación operativa

Antes de entrenar, revisar que cada clase tenga la cantidad esperada de
secuencias y que el GIF de referencia represente correctamente la seña. Si una
clase fue capturada en malas condiciones, conviene sobrescribirla antes de
entrenar el modelo.
