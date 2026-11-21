"""Run the full pipeline end to end:  python run_all.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import get_data, analysis, overbooking  # noqa: E402

for step in (get_data, analysis, overbooking):
    step.main()
print("\nDone. Figures in reports/figures/, tables in reports/tables/.")
