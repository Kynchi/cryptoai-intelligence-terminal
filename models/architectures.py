from __future__ import annotations

from typing import Any


DEEP_MODEL_NAMES = {
    "lstm",
    "gru",
    "bilstm",
    "cnn_lstm",
    "cnn_bilstm",
    "cnn_lstm_attention",
    "transformer",
    "temporal_fusion_transformer",
    "nbeats",
}


def _tensorflow():
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise RuntimeError(
            "TensorFlow is required for deep learning models. Install dependencies with "
            "`pip install -r requirements.txt`."
        ) from exc
    return tf


def build_deep_model(
    model_name: str,
    input_shape: tuple[int, int],
    output_dim: int,
    params: dict[str, Any],
):
    tf = _tensorflow()
    keras = tf.keras
    layers = keras.layers
    regularizers = keras.regularizers

    units = int(params.get("hidden_units", 96))
    dropout = float(params.get("dropout", 0.25))
    l2 = float(params.get("l2", 0.0001))
    filters = int(params.get("filters", 64))
    attention_dim = int(params.get("attention_dim", 64))

    inputs = keras.Input(shape=input_shape, name="ohlcv_feature_sequence")
    x = inputs

    if model_name == "lstm":
        x = layers.LSTM(units, kernel_regularizer=regularizers.l2(l2))(x)
    elif model_name == "gru":
        x = layers.GRU(units, kernel_regularizer=regularizers.l2(l2))(x)
    elif model_name == "bilstm":
        x = layers.Bidirectional(layers.LSTM(units, kernel_regularizer=regularizers.l2(l2)))(x)
    elif model_name == "cnn_lstm":
        x = layers.Conv1D(filters, kernel_size=3, padding="causal", activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.LSTM(units, kernel_regularizer=regularizers.l2(l2))(x)
    elif model_name == "cnn_bilstm":
        x = layers.Conv1D(filters, kernel_size=3, padding="causal", activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Bidirectional(layers.LSTM(units, kernel_regularizer=regularizers.l2(l2)))(x)
    elif model_name == "cnn_lstm_attention":
        x = layers.Conv1D(filters, kernel_size=3, padding="causal", activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.LSTM(units, return_sequences=True, kernel_regularizer=regularizers.l2(l2))(x)
        attention = layers.MultiHeadAttention(num_heads=4, key_dim=attention_dim, name="forecast_attention")(x, x)
        x = layers.Add()([x, attention])
        x = layers.LayerNormalization()(x)
        x = layers.GlobalAveragePooling1D()(x)
    elif model_name == "transformer":
        projected = layers.Dense(attention_dim)(x)
        attention = layers.MultiHeadAttention(num_heads=4, key_dim=attention_dim)(projected, projected)
        x = layers.Add()([projected, attention])
        x = layers.LayerNormalization()(x)
        feed_forward = layers.Dense(units, activation="relu", kernel_regularizer=regularizers.l2(l2))(x)
        x = layers.Add()([x, layers.Dense(attention_dim)(feed_forward)])
        x = layers.GlobalAveragePooling1D()(x)
    elif model_name == "temporal_fusion_transformer":
        variable_selection = layers.Dense(input_shape[-1], activation="sigmoid", name="variable_selection")(x)
        x = layers.Multiply()([x, variable_selection])
        x = layers.LSTM(units, return_sequences=True, kernel_regularizer=regularizers.l2(l2))(x)
        attention = layers.MultiHeadAttention(num_heads=4, key_dim=attention_dim, name="temporal_attention")(x, x)
        x = layers.Add()([x, attention])
        x = layers.LayerNormalization()(x)
        gated_value = layers.Dense(units, activation="elu")(x)
        gated_signal = layers.Dense(units, activation="sigmoid")(x)
        x = layers.Multiply()([gated_value, gated_signal])
        x = layers.GlobalAveragePooling1D()(x)
    elif model_name == "nbeats":
        x = layers.Flatten()(x)
        residual = x
        block_outputs = []
        for block in range(3):
            theta = residual
            for _ in range(3):
                theta = layers.Dense(units, activation="relu", kernel_regularizer=regularizers.l2(l2))(theta)
                theta = layers.BatchNormalization()(theta)
                theta = layers.Dropout(dropout)(theta)
            block_outputs.append(layers.Dense(output_dim, name=f"nbeats_forecast_{block}")(theta))
            residual = layers.Subtract()([residual, layers.Dense(int(residual.shape[-1]))(theta)])
        outputs = layers.Average(name="forecast_output")(block_outputs)
        model = keras.Model(inputs, outputs, name=model_name)
        return model
    else:
        supported = ", ".join(sorted(DEEP_MODEL_NAMES))
        raise ValueError(f"Unsupported deep model '{model_name}'. Supported: {supported}")

    x = layers.BatchNormalization()(x)
    x = layers.Dropout(dropout)(x)
    x = layers.Dense(units // 2 or 16, activation="relu", kernel_regularizer=regularizers.l2(l2))(x)
    x = layers.Dropout(dropout / 2)(x)
    outputs = layers.Dense(output_dim, name="forecast_output")(x)
    return keras.Model(inputs, outputs, name=model_name)


def compile_deep_model(model, params: dict[str, Any]):
    tf = _tensorflow()
    learning_rate = float(params.get("learning_rate", 0.001))
    optimizer_name = str(params.get("optimizer", "adam")).lower()
    optimizers = {
        "adam": tf.keras.optimizers.Adam,
        "nadam": tf.keras.optimizers.Nadam,
        "rmsprop": tf.keras.optimizers.RMSprop,
    }
    optimizer_cls = optimizers.get(optimizer_name, tf.keras.optimizers.Adam)
    model.compile(
        optimizer=optimizer_cls(learning_rate=learning_rate),
        loss=tf.keras.losses.Huber(),
        metrics=[tf.keras.metrics.MeanAbsoluteError(name="mae")],
    )
    return model
