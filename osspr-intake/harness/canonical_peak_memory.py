"""Peak memory of ``canonical_bytes`` on a 2,000-symbol provenance document.

``provenance_id`` hashes this document through ``canonical_bytes``. The
encoder first builds a tagged Python tree, then ``json.dumps`` it. The
bytes are specified exactly (tests lock them). A writer that emits those
same bytes without the tree can drop the extra peak.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure import peak_bytes, report

from investing_algorithm_framework.domain.backtesting.record_schemas import (
    validate_provenance,
)
from investing_algorithm_framework.domain.backtesting.records import (
    canonical_bytes,
)

SYMBOLS = 2_000


def build_document():
    document = {
        "version": 1,
        "algorithm_id": "cross-section",
        "study_id": "study-1",
        "window_id": "2023-2024",
        "engine_id": "vector",
        "strategies": [{
            "strategy_id": "cross-section",
            "version": "1",
            "code_digest": "sha256:source",
            "parameters": {"period": 20, "top": 50},
            "evaluator_version": "scalar-v1",
            "card_ids": ["card-ema"],
        }],
        "market_data": [{
            "symbol_id": f"SYM{i:04d}",
            "provider": "yahoo",
            "content_digest": f"sha256:{i:064x}",
            "start_us": 1672531200000000,
            "end_us": 1704067200000000,
            "timeframe": "1d",
            "adjustments": ["split", "dividend"],
        } for i in range(SYMBOLS)],
        "indicators": [{
            "name": name,
            "implementation": f"package.{name}",
            "version": "1",
            "parameters": {"period": period},
            "inputs": ["close"],
            "warmup": period * 3,
            "alignment": "bar_close",
            "missing_policy": "unavailable",
        } for name, period in (("ema", 20), ("rsi", 14), ("z_score", 60))],
        "execution": {
            "fees": 0.001,
            "slippage": 0.0005,
            "sizing": "volatility",
            "fill_timing": "next_bar",
            "risk": ["max_position"],
            "conflicts": "net",
            "seed": 1,
            "recording_policy": "full",
        },
        "environment": {
            "framework_version": "9.0.0a22",
            "dependencies": {"pandas": "2.3.3"},
            "platform": "linux",
        },
    }
    validate_provenance(document)
    return document


def main():
    document = build_document()
    report("baseline_value", peak_bytes(lambda: canonical_bytes(document)))


if __name__ == "__main__":
    main()
