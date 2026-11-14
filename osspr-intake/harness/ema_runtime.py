"""Baseline for ``_ema`` on one year of 1-minute closes.

``compute_indicator`` calls this for EMA, MACD, and Wilder RSI. The loop
walks a pandas Series, so every bar is boxed. A local change that runs the
same reset-on-gap recurrence over the NumPy buffer returns an equal Series
and drops most of that per-bar overhead.
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure import report, time_ms

from investing_algorithm_framework.services.indicator_engine import _ema

BARS = 525_600  # 365 days of 1-minute crypto bars
PERIOD = 20


def build_close():
    index = pd.date_range("2024-01-01", periods=BARS, freq="min", tz="UTC")
    values = 100 + np.cumsum(np.random.default_rng(0).normal(0, 0.05, BARS))
    # Missing minutes (halts, empty buckets) reset the recurrence.
    values[::50_000] = np.nan
    return pd.Series(values, index=index)


def main():
    close = build_close()
    report(
        "baseline_median_ms",
        time_ms(lambda: _ema(close, PERIOD), warmup=3),
    )


if __name__ == "__main__":
    main()
