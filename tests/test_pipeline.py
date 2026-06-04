from __future__ import annotations

from forecasting.preprocessing import build_sequence_dataset
from tests.test_indicators import sample_frame
from indicators.technical import add_technical_indicators


def test_sequence_dataset_supports_multi_output_horizons():
    df = add_technical_indicators(sample_frame(160))
    dataset = build_sequence_dataset(df, sequence_length=30, horizons=[1, 3, 7])
    assert dataset.X.shape[1:] == (30, len(dataset.feature_names))
    assert dataset.y.shape[1] == 3
    assert dataset.target_index == 0
