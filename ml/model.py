"""Definición del modelo LSTM para reconocimiento de secuencias."""

from typing import Tuple

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization


def construir_modelo(input_shape: Tuple[int, int], num_clases: int) -> Sequential:
    """Arquitectura: LSTM(64,rs) → BN → LSTM(32) → Drop(0.3) → Dense(64,relu) → Dense(N,softmax).

    Compila con ``sparse_categorical_crossentropy`` + Adam.
    """
    modelo = Sequential(
        [
            LSTM(64, return_sequences=True, input_shape=input_shape),
            BatchNormalization(),
            LSTM(32),
            Dropout(0.3),
            Dense(64, activation="relu"),
            Dense(num_clases, activation="softmax"),
        ]
    )
    modelo.compile(
        loss="sparse_categorical_crossentropy",
        optimizer="adam",
        metrics=["accuracy"],
    )
    return modelo
