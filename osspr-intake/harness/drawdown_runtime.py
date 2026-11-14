"""Baseline for ``get_drawdown_series`` on one year of 1-minute snapshots.

The vector engine records a portfolio snapshot per bar. This function first
builds a sorted equity-curve list, then walks it into a second list. One
pass from the snapshots into the result list keeps the same pairs and
skips that intermediate copy.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure import report, time_ms

from investing_algorithm_framework.domain.models.portfolio.portfolio_snapshot \
    import PortfolioSnapshot
from investing_algorithm_framework.services.metrics.drawdown import (
    get_drawdown_series,
)

BARS = 525_600


def build_snapshots():
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    step = timedelta(minutes=1)
    snapshots = []
    for i in range(BARS):
        # A rising account with a two-month drawdown, in bar order.
        value = 10_000.0 + (i % 20_000) * 0.35
        if 100_000 <= i < 180_000:
            value -= 2_500.0
        snapshots.append(PortfolioSnapshot(
            portfolio_id="primary",
            total_value=value,
            cash_flow=0.0,
            created_at=start + step * i,
        ))
    return snapshots


def main():
    snapshots = build_snapshots()
    report(
        "baseline_median_ms",
        time_ms(lambda: get_drawdown_series(snapshots), warmup=3),
    )


if __name__ == "__main__":
    main()
