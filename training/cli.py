from __future__ import annotations

import argparse
import json

from training.train import TrainingPipeline
from utils.logging import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Train crypto forecasting models.")
    parser.add_argument("--symbol", required=True, choices=["BTC", "ETH", "SOL", "XRP"])
    parser.add_argument("--model", default=None)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--sequence-length", type=int, default=None)
    args = parser.parse_args()

    setup_logging()
    overrides = {}
    if args.epochs is not None:
        overrides["epochs"] = args.epochs
    if args.sequence_length is not None:
        overrides["sequence_length"] = args.sequence_length

    result = TrainingPipeline().train(args.symbol, args.model, overrides=overrides)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
