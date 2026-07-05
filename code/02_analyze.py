"""Stage 2 — estimate convergence and emit result tables + in-text macros.

Reads   : data/derived/cross_section.parquet, panel_balanced.parquet
Writes  : tables/convergence_regressions.tex   (main regression table)
          tables/summary_stats.tex             (descriptives)
          tables/estimates.tex                 (in-text \\newcommand macros)
          data/derived/sigma_series.csv        (dispersion by year, for the figure)

Estimates absolute beta-convergence and sigma-convergence. (Conditional
beta-convergence is added later through the issue-driven loop; see LOG.md.)
Run via `python code/run_all.py`.
"""
from __future__ import annotations
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import config as C
import latexout as L


def implied_lambda(beta: float, T: int) -> float:
    """Solow convergence speed implied by beta: lambda = -ln(1+beta*T)/T.

    Defined only when 1+beta*T>0; returns NaN otherwise (i.e. no convergence).
    """
    z = 1.0 + beta * T
    return -np.log(z) / T if z > 0 else float("nan")


def half_life(lam: float) -> float:
    return np.log(2) / lam if lam and lam > 0 else float("nan")


def main() -> None:
    T = C.HORIZON
    cs = pd.read_parquet(C.DERIVED / "cross_section.parquet")
    panel = pd.read_parquet(C.DERIVED / "panel_balanced.parquet")

    # ---- absolute beta-convergence: g on log initial income -------------- #
    m_abs = smf.ols("g ~ y0", data=cs).fit(cov_type="HC1")
    b_abs = m_abs.params["y0"]
    lam_abs = implied_lambda(b_abs, T)

    # ---- sigma-convergence: cross-country dispersion of log income ------- #
    sigma = panel.groupby("year")["lgdppc"].std().rename("sigma")
    sigma.to_csv(C.DERIVED / "sigma_series.csv")
    years = sigma.index.values.astype(float)
    sigma_slope = np.polyfit(years, sigma.values, 1)[0]

    # ---- main regression table (one column for now) ---------------------- #
    L.regression_table(
        C.TABLES / "convergence_regressions.tex",
        models=[m_abs],
        column_labels=["Absolute"],
        coef_order=["y0", "Intercept"],
        coef_names={"y0": r"Log initial GDP p.c. ($\beta$)", "Intercept": "Constant"},
        extra_rows=[
            (r"Implied $\lambda$ (\%/yr)", [L.num(implied_lambda(b_abs, T) * 100, 2)]),
            ("Half-life (yrs)", [L.num(half_life(lam_abs), 0)]),
            ("Observations", [str(int(m_abs.nobs))]),
            (r"$R^2$", [L.num(m_abs.rsquared, 3)]),
        ],
        caption=(f"Beta-convergence of real GDP per capita, {C.START_YEAR}--{C.END_YEAR}. "
                 f"Dependent variable: average annual log growth. "
                 f"Heteroskedasticity-robust (HC1) standard errors in parentheses."),
        label="tab:convergence",
        notes=r"$^{*}p<0.1$, $^{**}p<0.05$, $^{***}p<0.01$.",
    )

    # ---- summary statistics --------------------------------------------- #
    desc = (
        cs[["y0", "y1", "g", "csh_i", "n", "delta", "hc"]]
        .describe().T[["count", "mean", "std", "min", "max"]]
    )
    desc.insert(0, "Variable", [
        "Log GDP p.c., initial", "Log GDP p.c., final", "Avg. annual growth",
        "Investment share", "Population growth", "Depreciation rate", "Human capital",
    ])
    desc["count"] = desc["count"].astype(int)
    L.dataframe_table(
        C.TABLES / "summary_stats.tex",
        desc.round(3),
        caption="Summary statistics (country cross-section).",
        label="tab:summary",
        index=False,
    )

    # ---- in-text macros -------------------------------------------------- #
    L.write_macros(C.TABLES / "estimates.tex", {
        "startYear": str(C.START_YEAR),
        "finalYear": str(C.END_YEAR),
        "horizon": str(T),
        "Nabs": str(int(m_abs.nobs)),
        "betaAbs": L.num(b_abs, 4),
        "seAbs": L.num(m_abs.bse["y0"], 4),
        "pAbs": L.num(m_abs.pvalues["y0"], 3),
        "rsqAbs": L.num(m_abs.rsquared, 3),
        "lambdaAbs": L.num(lam_abs * 100, 2),
        "halflifeAbs": L.num(half_life(lam_abs), 0),
        "sigmaStart": L.num(sigma.iloc[0], 3),
        "sigmaEnd": L.num(sigma.iloc[-1], 3),
        "sigmaSlope": L.num(sigma_slope, 4),
        "Nsigma": str(panel["countrycode"].nunique()),
    })

    print(f"[02_analyze] absolute beta={b_abs:.4f} (p={m_abs.pvalues['y0']:.3f}), "
          f"lambda={lam_abs*100:.2f}%/yr; sigma {sigma.iloc[0]:.3f}->{sigma.iloc[-1]:.3f}")


if __name__ == "__main__":
    main()
