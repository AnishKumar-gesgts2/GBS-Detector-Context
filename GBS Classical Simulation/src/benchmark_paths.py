"""Output locations for fresh reproductions and published-data analysis."""
import os
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('GBS_BENCHMARK_OUTPUT', str(PROJECT / 'results' / 'smoke_v1'))).resolve()
