"""Timing and peak-memory helpers for the intake harnesses.

Noise is the full spread of the recorded runs: (max - min) / median * 100.
One untimed warmup call runs first. Each recorded call is preceded by a
garbage collection so the spread is the function, not leftover garbage.
"""
import gc
import statistics
import time
import tracemalloc

RUNS = 7
WARMUP = 1


def summarize(samples):
    median = statistics.median(samples)
    noise_pct = (max(samples) - min(samples)) / median * 100.0
    return median, noise_pct


def time_ms(fn, runs=RUNS, warmup=WARMUP):
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(runs):
        gc.collect()
        started = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - started) * 1000.0)
    return samples


def peak_bytes(fn, runs=RUNS, warmup=WARMUP):
    """Peak Python bytes traced while ``fn`` runs, excluding earlier input."""
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(runs):
        gc.collect()
        tracemalloc.start()
        tracemalloc.reset_peak()
        result = fn()
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        del result
        samples.append(peak)
    return samples


def report(kind, samples):
    median, noise_pct = summarize(samples)
    if kind.endswith("_bytes"):
        rendered = [int(sample) for sample in samples]
        median_text = str(int(median) if median == int(median) else median)
    else:
        rendered = [round(sample, 4) for sample in samples]
        median_text = f"{median:.4f}"
    print(
        f"RESULT {kind}={median_text} noise_pct={noise_pct:.4f} "
        f"runs={rendered}"
    )
    return median, noise_pct
