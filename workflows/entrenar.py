"""Workflow de entrenamiento del modelo LSTM. Requiere permiso 'entrenar'."""

import json
import logging
import os
import pickle
import random
import warnings

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
logging.getLogger("tensorflow").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", module="tensorflow")

import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ModelCheckpoint,
    ReduceLROnPlateau,
)

from auth import log_event, requerir, usuario_actual
from core.config import config
from core import ui
from ml.data_io import DatasetError, cargar_datos
from ml.model import construir_modelo

tf.get_logger().setLevel("ERROR")


def _set_seeds(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def main() -> None:
    user = usuario_actual()
    if user is None:
        ui.error("No hay sesión activa")
        return
    requerir("entrenar", user.rol)

    ui.title("Entrenamiento del modelo", "LSTM para reconocimiento de secuencias")
    ui.step("Cargando dataset")
    try:
        X, y, etiquetas = cargar_datos()
    except DatasetError as e:
        ui.error(str(e))
        return

    ui.metric_rows(
        [
            ("Clases", ", ".join(etiquetas)),
            ("Total muestras", len(X)),
            ("Shape entrada", X.shape),
        ]
    )

    if len(set(y)) < 2:
        ui.error("Se necesitan al menos 2 clases con datos para entrenar.")
        return

    log_event(
        user.username,
        "train_start",
        f"clases={len(etiquetas)} muestras={len(X)}",
    )

    _set_seeds(config.TRAIN_RANDOM_SEED)

    # Split estratificado: 70/15/15 si alcanzan muestras, sino 80/20 sin test.
    X_test = y_test = None
    try:
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y,
            test_size=config.TRAIN_TEST_SIZE,
            random_state=config.TRAIN_RANDOM_SEED,
            stratify=y,
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=config.TRAIN_VAL_SIZE,
            random_state=config.TRAIN_RANDOM_SEED,
            stratify=y_temp,
        )
        ui.info(
            f"Split estratificado: train={len(X_train)} val={len(X_val)} test={len(X_test)}"
        )
    except ValueError:
        ui.warning("Pocas muestras para holdout test. Usando split 80/20 sin test.")
        X_train, X_val, y_train, y_val = train_test_split(
            X, y,
            test_size=0.2,
            random_state=config.TRAIN_RANDOM_SEED,
            stratify=y,
        )
        X_test, y_test = None, None

    ui.step("Construyendo modelo LSTM")
    modelo = construir_modelo(
        (config.FRAMES_PER_SEQUENCE, config.FEATURES),
        len(etiquetas),
    )

    os.makedirs(config.MODELS_DIR, exist_ok=True)
    callbacks = [
        EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=5),
        ModelCheckpoint(config.MODEL_PATH, monitor="val_loss", save_best_only=True),
    ]

    ui.step(
        f"Entrenando hasta {config.TRAIN_EPOCHS} epochs "
        f"(batch={config.TRAIN_BATCH_SIZE})"
    )
    history = modelo.fit(
        X_train, y_train,
        epochs=config.TRAIN_EPOCHS,
        batch_size=config.TRAIN_BATCH_SIZE,
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        verbose=2,
    )

    ui.section("Métricas de validación")
    val_pred = np.argmax(modelo.predict(X_val, verbose=0), axis=1)
    print(
        classification_report(
            y_val, val_pred, target_names=etiquetas, zero_division=0
        )
    )

    if X_test is not None:
        ui.section("Métricas de test")
        test_pred = np.argmax(modelo.predict(X_test, verbose=0), axis=1)
        print(
            classification_report(
                y_test, test_pred, target_names=etiquetas, zero_division=0
            )
        )
        cm = confusion_matrix(y_test, test_pred).tolist()
        ui.info(f"Matriz de confusión (test): {cm}")

    # Persistencia
    modelo.save(config.MODEL_PATH)
    with open(config.LABELS_PATH, "wb") as f:
        pickle.dump(etiquetas, f)

    history_serializable = {
        k: [float(v) for v in vals] for k, vals in history.history.items()
    }
    with open(config.HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history_serializable, f, indent=2)

    epochs_corridas = len(history.history.get("loss", []))
    log_event(
        user.username,
        "train_finish",
        f"clases={len(etiquetas)} epochs={epochs_corridas}",
    )

    ui.section("Archivos generados")
    ui.success(f"Modelo: {config.MODEL_PATH}")
    ui.success(f"Etiquetas: {config.LABELS_PATH}")
    ui.success(f"Historia: {config.HISTORY_PATH}")
