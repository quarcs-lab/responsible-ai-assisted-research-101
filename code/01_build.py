"""Stage 1 — build the analysis datasets from PWT 11.0.

Reads   : data/raw/pwt110.dta   (immutable)
Writes  : data/derived/cross_section.parquet       (main window, one row/country)
          data/derived/cross_section_1990.parquet  (1990-2019 robustness window)
          data/derived/panel_balanced.parquet      (country x year, for sigma)
          tables/attrition.tex                      (sample-construction table)

Every country dropped from the sample is accounted for in the attrition table
(CLAUDE.md: no silent sample construction). Run via `python code/run_all.py`.
"""
from __future__ import annotations
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import config as C
import latexout as L


def build_cross_section(df: pd.DataFrame, t0: int, t1: int):
    """Return (cross_section, sample_ids, attrition_counts) for the window [t0, t1].

    cross_section is indexed by countrycode with the level, growth, and the
    window-averaged Solow controls. attrition_counts is a list of stage rows.
    """
    T = t1 - t0
    g0 = df[df.year == t0].set_index("countrycode")["gdppc"]
    g1 = df[df.year == t1].set_index("countrycode")["gdppc"]
    p0 = df[df.year == t0].set_index("countrycode")["pop"]
    p1 = df[df.year == t1].set_index("countrycode")["pop"]
    outlier = (
        df[df.year.isin([t0, t1])]
        .assign(is_out=lambda d: d["i_outlier"].astype(str).eq("Outlier"))
        .groupby("countrycode")["is_out"].any()
    )

    n0 = df["countrycode"].nunique()
    s1 = g0[(g0.notna()) & (g0 > 0)].index
    s2 = [c for c in s1 if c in g1.index and pd.notna(g1[c]) and g1[c] > 0]
    s3 = [c for c in s2 if not (C.DROP_OUTLIERS and outlier.get(c, False))]

    win = df[(df.year >= t0) & (df.year <= t1)]
    cs = pd.DataFrame(index=pd.Index(s3, name="countrycode"))
    cs["country"] = df.drop_duplicates("countrycode").set_index("countrycode")["country"].reindex(s3)
    cs["gdppc0"] = g0.reindex(s3)
    cs["gdppc1"] = g1.reindex(s3)
    cs["y0"] = np.log(cs["gdppc0"])          # log initial GDP per capita
    cs["y1"] = np.log(cs["gdppc1"])
    cs["g"] = (cs["y1"] - cs["y0"]) / T      # average annual log growth
    cs["csh_i"] = win.groupby("countrycode")["csh_i"].mean().reindex(s3)
    cs["delta"] = win.groupby("countrycode")["delta"].mean().reindex(s3)
    cs["hc"] = win.groupby("countrycode")["hc"].mean().reindex(s3)
    cs["n"] = (np.log(p1.reindex(s3)) - np.log(p0.reindex(s3))) / T

    # Solow regressors (logs); guard the log domain
    cs["lnsi"] = np.log(cs["csh_i"].where(cs["csh_i"] > 0))
    cs["lnngd"] = np.log((cs["n"] + C.G_TECH + cs["delta"]).where(lambda s: s > 0))
    cs["lnhc"] = np.log(cs["hc"].where(cs["hc"] > 0))

    cond_ok = cs[["g", "y0", "lnsi", "lnngd", "lnhc"]].replace([np.inf, -np.inf], np.nan).notna().all(axis=1)
    n_cond = int(cond_ok.sum())

    attrition = [
        ["0", "PWT 11.0: all economies", n0, ""],
        ["1", f"GDP p.c. observed and positive in {t0}", len(s1), n0 - len(s1)],
        ["2", f"GDP p.c. observed and positive in {t1}", len(s2), len(s1) - len(s2)],
        ["3", "Not a PPP outlier at either endpoint", len(s3), len(s2) - len(s3)],
        ["4", "Solow controls present (conditional sample)", n_cond, len(s3) - n_cond],
    ]
    assert len(s3) + (n0 - len(s1)) + (len(s1) - len(s2)) + (len(s2) - len(s3)) == n0
    return cs, s3, attrition


def main() -> None:
    T0, T1, T = C.START_YEAR, C.END_YEAR, C.HORIZON
    assert T == 59, f"growth horizon must be {T1}-{T0}=59 intervals, got {T}"

    df = pd.read_stata(C.RAW)
    assert df["year"].dtype.kind in "iuf", "year should be numeric"
    df["gdppc"] = df[C.INCOME_MEASURE] / df["pop"]

    # main window (1960-2019) and a robustness window (1990-2019)
    cs, s3, attrition = build_cross_section(df, T0, T1)
    cs_recent, _, _ = build_cross_section(df, 1990, T1)

    # balanced panel (main-window sample) for sigma-convergence
    bal = df[(df.year >= T0) & (df.year <= T1) & df.countrycode.isin(s3)].copy()
    bal["lgdppc"] = np.log(bal["gdppc"].where(bal["gdppc"] > 0))
    complete = bal.dropna(subset=["lgdppc"]).groupby("countrycode")["year"].nunique()
    keep = complete[complete == (T + 1)].index
    panel = bal[bal.countrycode.isin(keep)][["countrycode", "year", "lgdppc"]].copy()

    # write outputs
    C.DERIVED.mkdir(parents=True, exist_ok=True)
    cs.reset_index().to_parquet(C.DERIVED / "cross_section.parquet", index=False)
    cs_recent.reset_index().to_parquet(C.DERIVED / "cross_section_1990.parquet", index=False)
    panel.to_parquet(C.DERIVED / "panel_balanced.parquet", index=False)

    attrition_df = pd.DataFrame(attrition, columns=["Stage", "Criterion", "Countries", "Dropped"])
    L.dataframe_table(
        C.TABLES / "attrition.tex",
        attrition_df,
        caption="Sample construction and attrition.",
        label="tab:attrition",
        index=False,
        notes=(f"Income per capita is {C.INCOME_MEASURE}/pop from PWT 11.0 (2021 US\\$). "
               f"The conditional sample (stage 4) additionally requires the Solow "
               f"controls (investment share, population growth, human capital)."),
    )

    print(f"[01_build] main sample {len(s3)} countries; "
          f"1990-2019 sample {len(cs_recent)} countries; balanced panel {len(keep)} countries")


if __name__ == "__main__":
    main()
