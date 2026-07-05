"""Stage 3 — figures.

Reads   : data/derived/cross_section.parquet, data/derived/sigma_series.csv
Writes  : figures/beta_convergence.pdf   (growth vs. initial income, with OLS fit)
          figures/sigma_convergence.pdf  (dispersion of log income over time)

Run via `python code/run_all.py`.
"""
from __future__ import annotations
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # no display needed; write PDFs directly
import matplotlib.pyplot as plt

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import config as C


def main() -> None:
    T = C.HORIZON
    cs = pd.read_parquet(C.DERIVED / "cross_section.parquet").dropna(subset=["y0", "g"])
    sigma = pd.read_csv(C.DERIVED / "sigma_series.csv")

    # ---- Figure 1: absolute beta-convergence scatter --------------------- #
    slope, intercept = np.polyfit(cs["y0"], cs["g"], 1)
    z = 1 + slope * T
    lam = -np.log(z) / T if z > 0 else float("nan")

    fig, ax = plt.subplots(figsize=(6, 4.2))
    ax.scatter(cs["y0"], cs["g"], s=22, alpha=0.7, edgecolor="none")
    xs = np.linspace(cs["y0"].min(), cs["y0"].max(), 100)
    ax.plot(xs, intercept + slope * xs, color="crimson", lw=1.8)
    ax.set_xlabel(f"Log real GDP per capita, {C.START_YEAR} (2021 US$)")
    ax.set_ylabel(f"Average annual growth, {C.START_YEAR}–{C.END_YEAR}")
    ax.set_title("Absolute β-convergence")
    ax.annotate(
        f"$\\beta$ = {slope:.4f}\n$\\lambda$ = {lam*100:.2f}%/yr\nN = {len(cs)}",
        xy=(0.97, 0.95), xycoords="axes fraction", ha="right", va="top",
        fontsize=9, bbox=dict(boxstyle="round", fc="white", ec="0.7"),
    )
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(C.FIGURES / "beta_convergence.pdf", bbox_inches="tight")
    plt.close(fig)

    # ---- Figure 2: sigma-convergence over time --------------------------- #
    fig, ax = plt.subplots(figsize=(6, 4.2))
    ax.plot(sigma["year"], sigma["sigma"], color="steelblue", lw=1.8)
    ax.set_xlabel("Year")
    ax.set_ylabel("Std. dev. of log GDP per capita")
    ax.set_title("σ-convergence (cross-country dispersion)")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(C.FIGURES / "sigma_convergence.pdf", bbox_inches="tight")
    plt.close(fig)

    print(f"[03_figures] wrote beta_convergence.pdf and sigma_convergence.pdf")


if __name__ == "__main__":
    main()
