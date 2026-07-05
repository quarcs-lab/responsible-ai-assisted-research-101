"""Stage 1 — build the analysis datasets from PWT 11.0.

Reads   : data/raw/pwt110.dta   (immutable)
Writes  : data/derived/cross_section.parquet   (one row per country)
          data/derived/panel_balanced.parquet  (country x year, for sigma)
          tables/attrition.tex                  (sample-construction table)

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


def main() -> None:
    T0, T1, T = C.START_YEAR, C.END_YEAR, C.HORIZON
    assert T == 59, f"growth horizon must be {T1}-{T0}=59 intervals, got {T}"

    df = pd.read_stata(C.RAW)
    # sanity: units. PWT 11.0 real values are in 2021 US$; pop in millions.
    assert df["year"].dtype.kind in "iuf", "year should be numeric"
    df["gdppc"] = df[C.INCOME_MEASURE] / df["pop"]

    # ---- endpoint series ------------------------------------------------- #
    g0 = df[df.year == T0].set_index("countrycode")["gdppc"]
    g1 = df[df.year == T1].set_index("countrycode")["gdppc"]
    p0 = df[df.year == T0].set_index("countrycode")["pop"]
    p1 = df[df.year == T1].set_index("countrycode")["pop"]
    outlier = (
        df[df.year.isin([T0, T1])]
        .assign(is_out=lambda d: d["i_outlier"].astype(str).eq("Outlier"))
        .groupby("countrycode")["is_out"].any()
    )

    # ---- attrition (each filter is a row; dropped counts must reconcile) -- #
    n0 = df["countrycode"].nunique()
    s1 = g0[(g0.notna()) & (g0 > 0)].index
    s2 = [c for c in s1 if c in g1.index and pd.notna(g1[c]) and g1[c] > 0]
    s3 = [c for c in s2 if not (C.DROP_OUTLIERS and outlier.get(c, False))]

    # window-averaged Solow controls (over the full 1960-2019 window)
    win = df[(df.year >= T0) & (df.year <= T1)]
    csh_i = win.groupby("countrycode")["csh_i"].mean()
    delta = win.groupby("countrycode")["delta"].mean()
    hc = win.groupby("countrycode")["hc"].mean()

    cs = pd.DataFrame(index=pd.Index(s3, name="countrycode"))
    cs["country"] = df.drop_duplicates("countrycode").set_index("countrycode")["country"].reindex(s3)
    cs["gdppc0"] = g0.reindex(s3)
    cs["gdppc1"] = g1.reindex(s3)
    cs["y0"] = np.log(cs["gdppc0"])          # log initial GDP per capita
    cs["y1"] = np.log(cs["gdppc1"])
    cs["g"] = (cs["y1"] - cs["y0"]) / T      # average annual log growth
    cs["csh_i"] = csh_i.reindex(s3)
    cs["delta"] = delta.reindex(s3)
    cs["hc"] = hc.reindex(s3)
    cs["n"] = (np.log(p1.reindex(s3)) - np.log(p0.reindex(s3))) / T

    # Solow regressors (logs); guard the log domain
    cs["lnsi"] = np.log(cs["csh_i"].where(cs["csh_i"] > 0))
    cs["lnngd"] = np.log((cs["n"] + C.G_TECH + cs["delta"]).where(lambda s: s > 0))
    cs["lnhc"] = np.log(cs["hc"].where(cs["hc"] > 0))

    # the conditional sample = rows with all Solow regressors present
    cond_ok = cs[["g", "y0", "lnsi", "lnngd", "lnhc"]].replace([np.inf, -np.inf], np.nan).notna().all(axis=1)
    n_cond = int(cond_ok.sum())

    attrition = pd.DataFrame(
        [
            ["0", "PWT 11.0: all economies", n0, ""],
            ["1", f"GDP p.c. observed and positive in {T0}", len(s1), n0 - len(s1)],
            ["2", f"GDP p.c. observed and positive in {T1}", len(s2), len(s1) - len(s2)],
            ["3", "Not a PPP outlier at either endpoint", len(s3), len(s2) - len(s3)],
            ["4", "Solow controls present (conditional sample)", n_cond, len(s3) - n_cond],
        ],
        columns=["Stage", "Criterion", "Countries", "Dropped"],
    )
    # invariant: nothing vanishes unaccounted for
    assert len(s3) + (n0 - len(s1)) + (len(s1) - len(s2)) + (len(s2) - len(s3)) == n0

    # ---- balanced panel for sigma-convergence ---------------------------- #
    bal = df[(df.year >= T0) & (df.year <= T1) & df.countrycode.isin(s3)].copy()
    bal["lgdppc"] = np.log(bal["gdppc"].where(bal["gdppc"] > 0))
    complete = bal.dropna(subset=["lgdppc"]).groupby("countrycode")["year"].nunique()
    keep = complete[complete == (T + 1)].index
    panel = bal[bal.countrycode.isin(keep)][["countrycode", "year", "lgdppc"]].copy()

    # ---- write outputs --------------------------------------------------- #
    C.DERIVED.mkdir(parents=True, exist_ok=True)
    cs.reset_index().to_parquet(C.DERIVED / "cross_section.parquet", index=False)
    panel.to_parquet(C.DERIVED / "panel_balanced.parquet", index=False)
    L.dataframe_table(
        C.TABLES / "attrition.tex",
        attrition,
        caption="Sample construction and attrition.",
        label="tab:attrition",
        index=False,
        notes=(f"Income per capita is {C.INCOME_MEASURE}/pop from PWT 11.0 (2021 US\\$). "
               f"The conditional sample (stage 4) additionally requires the Solow "
               f"controls (investment share, population growth, human capital)."),
    )

    print(f"[01_build] absolute sample: {len(s3)} countries; "
          f"conditional sample: {n_cond}; balanced panel: {len(keep)} countries x {T+1} years")


if __name__ == "__main__":
    main()
