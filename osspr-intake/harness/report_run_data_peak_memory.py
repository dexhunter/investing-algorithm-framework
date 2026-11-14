"""Peak memory of ``BacktestReport._build_run_data`` on a year of 15-minute bars.

The dashboard formats every equity, drawdown, and rolling-Sharpe point
into a ``[value, date]`` list, then ``_downsample`` keeps 300 of them.
Selecting the indexes first and formatting only the kept points returns
the same run-data dict without holding the full string lists.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure import peak_bytes, report

from investing_algorithm_framework.app.reporting.backtest_report import (
    BacktestReport,
)
from investing_algorithm_framework.domain import (
    Backtest,
    BacktestDateRange,
    BacktestMetrics,
    BacktestRun,
    BacktestWindow,
    PortfolioSnapshot,
)

# 2024 is a leap year: 366 days of 15-minute bars, ending on the next hour.
BARS = 366 * 24 * 4


def build_report():
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2025, 1, 1, tzinfo=timezone.utc)
    step = timedelta(minutes=15)
    equity = []
    drawdown = []
    twr_equity = []
    twr_drawdown = []
    rolling_sharpe = []
    for i in range(BARS):
        stamp = start + step * i
        equity.append((10_000.0 + (i % 8_000) * 0.4, stamp))
        drawdown.append((-((i % 400) / 4_000.0), stamp))
        twr_equity.append((1.0 + i / BARS, stamp))
        twr_drawdown.append((-((i % 250) / 5_000.0), stamp))
        rolling_sharpe.append((0.4 + (i % 120) / 100.0, stamp))
    window = BacktestWindow(train_range=BacktestDateRange(
        start_date=start, end_date=end, name="y2024",
    ))
    metrics = BacktestMetrics(
        backtest_window=window,
        equity_curve=equity,
        drawdown_series=drawdown,
        twr_equity_curve=twr_equity,
        twr_drawdown_series=twr_drawdown,
        rolling_sharpe_ratio=rolling_sharpe,
        monthly_returns=[
            (0.012, datetime(2024, month, 1, tzinfo=timezone.utc))
            for month in range(1, 13)
        ],
        yearly_returns=[(0.18, datetime(2024, 12, 31, tzinfo=timezone.utc))],
        total_net_gain=1_800.0,
        cagr=0.18,
        sharpe_ratio=1.4,
        sortino_ratio=1.9,
        max_drawdown=0.12,
    )
    run = BacktestRun(
        backtest_window=window,
        orders=[],
        trades=[],
        positions=[],
        portfolio_snapshots=[
            PortfolioSnapshot(
                created_at=start, total_value=10_000.0,
                trading_symbol="USD", unallocated=10_000.0,
            ),
            PortfolioSnapshot(
                created_at=end, total_value=11_800.0,
                trading_symbol="USD", unallocated=2_400.0,
            ),
        ],
        initial_unallocated=10_000.0,
        created_at=start,
        backtest_metrics=metrics,
    )
    backtest = Backtest(
        algorithm_id="intraday15", vector_runs=[run], risk_free_rate=0.02,
    )
    return BacktestReport(backtest)


def main():
    report_obj = build_report()
    report(
        "baseline_value",
        peak_bytes(report_obj._build_run_data),
    )


if __name__ == "__main__":
    main()
