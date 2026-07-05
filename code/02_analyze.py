"""Stage 2 — estimate convergence and emit result tables + in-text macros.

Reads   : data/derived/cross_section.parquet, cross_section_1990.parquet,
          panel_balanced.parquet
Writes  : tables/convergence_regressions.tex   (main regression table)
          tables/summary_stats.tex             (descriptives)
          tables/estimates.tex                 (in-text \\newcommand macros)
          data/derived/sigma_series.csv        (dispersion by year, for the figure)

Estimates absolute AND conditional beta-convergence (with the Solow controls) and
sigma-convergence, plus a 1990-2019 robustness check. Run via `python code/run_all.py`.
"""
from __future__ import annotations
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import config as C
import latexout as L

COND_FORMULA = "g ~ y0 + lnsi + lnngd + lnhc"


def implied_lambda(beta: float, T: int) -> float:
    """Solow convergence speed implied by beta: lambda = -ln(1+beta*T)/T.

    Defined only when 1+beta*T>0; returns NaN otherwise (i.e. no convergence).
    """
    z = 1.0 + beta * T
    return -np.log(z) / T if z > 0 else float("nan")


def half_life(lam: float) -> float:
    return np.log(2) / lam if lam and lam > 0 else float("nan")


def pfmt(p: float) -> str:
    """A LaTeX-ready p-value fragment, e.g. '< 0.001' or '= 0.165'.

    Used inside math mode as `$p \\pAbs$`, so 'p = 0.000' never appears.
    """
    return "< 0.001" if p < 0.001 else f"= {p:.3f}"


def cond_sample(cs: pd.DataFrame) -> pd.DataFrame:
    """Rows with all Solow regressors present (the conditional sample)."""
    return cs.replace([np.inf, -np.inf], np.nan).dropna(
        subset=["g", "y0", "lnsi", "lnngd", "lnhc"])


def main() -> None:
    T = C.HORIZON
    cs = pd.read_parquet(C.DERIVED / "cross_section.parquet")
    cs_recent = pd.read_parquet(C.DERIVED / "cross_section_1990.parquet")
    panel = pd.read_parquet(C.DERIVED / "panel_balanced.parquet")

    csc = cond_sample(cs)                       # common/conditional sample (main window)
    csc_recent = cond_sample(cs_recent)         # conditional sample, 1990-2019

    # ---- models --------------------------------------------------------- #
    m_abs = smf.ols("g ~ y0", data=cs).fit(cov_type="HC1")            # absolute, full
    m_abs_c = smf.ols("g ~ y0", data=csc).fit(cov_type="HC1")         # absolute, common sample
    m_cond = smf.ols(COND_FORMULA, data=csc).fit(cov_type="HC1")     # conditional
    m_cond_r = smf.ols(COND_FORMULA, data=csc_recent).fit(cov_type="HC1")  # conditional, 1990-2019

    b_abs = m_abs.params["y0"]
    b_cond = m_cond.params["y0"]
    b_cond_r = m_cond_r.params["y0"]
    lam_abs = implied_lambda(b_abs, T)
    lam_cond = implied_lambda(b_cond, T)
    lam_cond_r = implied_lambda(b_cond_r, 2019 - 1990)

    # ---- sigma-convergence ---------------------------------------------- #
    sigma = panel.groupby("year")["lgdppc"].std().rename("sigma")
    sigma.to_csv(C.DERIVED / "sigma_series.csv")
    sigma_slope = np.polyfit(sigma.index.values.astype(float), sigma.values, 1)[0]

    # ---- main regression table (absolute | absolute-common | conditional) #
    models = [m_abs, m_abs_c, m_cond]
    L.regression_table(
        C.TABLES / "convergence_regressions.tex",
        models=models,
        column_labels=["Absolute", "Absolute", "Conditional"],
        coef_order=["y0", "lnsi", "lnngd", "lnhc", "Intercept"],
        coef_names={
            "y0": r"Log initial GDP p.c. ($\beta$)",
            "lnsi": r"$\ln$(investment share)",
            "lnngd": r"$\ln(n+g+\delta)$",
            "lnhc": r"$\ln$(human capital)",
            "Intercept": "Constant",
        },
        extra_rows=[
            (r"Sample", ["Full", "Common", "Common"]),
            (r"Implied $\lambda$ (\%/yr)",
             [L.num(lam_abs * 100, 2), L.num(implied_lambda(m_abs_c.params['y0'], T) * 100, 2),
              L.num(lam_cond * 100, 2)]),
            ("Half-life (yrs)",
             [L.num(half_life(lam_abs), 0), L.num(half_life(implied_lambda(m_abs_c.params['y0'], T)), 0),
              L.num(half_life(lam_cond), 0)]),
            ("Observations", [str(int(m.nobs)) for m in models]),
            (r"$R^2$", [L.num(m.rsquared, 3) for m in models]),
        ],
        caption=(f"Absolute and conditional beta-convergence of real GDP per capita, "
                 f"{C.START_YEAR}--{C.END_YEAR}. Dependent variable: average annual log "
                 f"growth. Heteroskedasticity-robust (HC1) standard errors in parentheses."),
        label="tab:convergence",
        notes=(r"Column 2 re-estimates the absolute model on the conditional sample for "
               r"comparability. $^{*}p<0.1$, $^{**}p<0.05$, $^{***}p<0.01$."),
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
        # absolute
        "Nabs": str(int(m_abs.nobs)),
        "betaAbs": L.num(b_abs, 4),
        "seAbs": L.num(m_abs.bse["y0"], 4),
        "pAbs": pfmt(m_abs.pvalues["y0"]),
        "rsqAbs": L.num(m_abs.rsquared, 3),
        "lambdaAbs": L.num(lam_abs * 100, 2),
        "halflifeAbs": L.num(half_life(lam_abs), 0),
        # conditional
        "Ncond": str(int(m_cond.nobs)),
        "betaCond": L.num(b_cond, 4),
        "seCond": L.num(m_cond.bse["y0"], 4),
        "pCond": pfmt(m_cond.pvalues["y0"]),
        "rsqCond": L.num(m_cond.rsquared, 3),
        "rateCond": L.num(lam_cond * 100, 2),
        "halflifeCond": L.num(half_life(lam_cond), 0),
        "hcCoef": L.num(m_cond.params["lnhc"], 3),
        # conditional, 1990-2019 robustness
        "NcondRecent": str(int(m_cond_r.nobs)),
        "betaCondRecent": L.num(b_cond_r, 4),
        "rateCondRecent": L.num(lam_cond_r * 100, 2),
        # sigma
        "sigmaStart": L.num(sigma.iloc[0], 3),
        "sigmaEnd": L.num(sigma.iloc[-1], 3),
        "sigmaSlope": L.num(sigma_slope, 4),
        "Nsigma": str(panel["countrycode"].nunique()),
    })

    print(f"[02_analyze] abs beta={b_abs:.4f} (p={m_abs.pvalues['y0']:.3f}); "
          f"cond beta={b_cond:.4f} (p={m_cond.pvalues['y0']:.3f}), rate={lam_cond*100:.2f}%/yr; "
          f"cond 1990-2019 rate={lam_cond_r*100:.2f}%/yr; sigma {sigma.iloc[0]:.3f}->{sigma.iloc[-1]:.3f}")


if __name__ == "__main__":
    main()
