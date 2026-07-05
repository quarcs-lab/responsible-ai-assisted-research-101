"""Central configuration for the Solow-convergence pipeline.

Paths and parameters only — no logic lives here. To reconfigure the study
(different income measure, window, or assumed technical progress), edit the
constants below and re-run `python code/run_all.py`. Every methodological choice
encoded here is documented, with alternatives, in DECISIONS.md.
"""
from __future__ import annotations
import pathlib

# --- paths (everything is relative to the repo root, resolved from this file) ---
ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "pwt110.dta"
DERIVED = ROOT / "data" / "derived"
TABLES = ROOT / "tables"
FIGURES = ROOT / "figures"

# --- methodological parameters (see DECISIONS.md D-0001..D-0004) ---
# Income per capita is INCOME_MEASURE / pop. rgdpna = real GDP at constant 2021
# national prices, PWT's recommended series for growth comparisons over time.
INCOME_MEASURE = "rgdpna"          # alternatives: "rgdpo", "rgdpe" (robustness)
START_YEAR = 1960                  # canonical Barro/MRW start with broad coverage
END_YEAR = 2019                    # ends before the COVID-19 GDP collapse
G_TECH = 0.02                      # assumed rate of technical progress (MRW convention)
DROP_OUTLIERS = True              # drop endpoint observations flagged i_outlier

# Derived constant: growth horizon in years (intervals, not endpoints).
HORIZON = END_YEAR - START_YEAR    # 59
