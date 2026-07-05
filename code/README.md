# `code/` — analysis scripts

Numbered scripts that run in order. `run_all.py` executes the whole pipeline and
regenerates every output from `data/raw/` with no manual steps.

| Script | Reads | Writes |
|--------|-------|--------|
| `config.py` | — | paths + parameters (no logic; edit this to reconfigure) |
| `01_build.py` | `data/raw/pwt110.dta` | `data/derived/*.parquet`, `tables/attrition.tex` |
| `02_analyze.py` | `data/derived/*.parquet` | `tables/convergence_regressions.tex`, `tables/summary_stats.tex`, `tables/estimates.tex`, `data/derived/sigma_series.csv` |
| `03_figures.py` | `data/derived/*.parquet` | `figures/beta_convergence.pdf`, `figures/sigma_convergence.pdf` |
| `latexout.py` | — | helper functions for emitting LaTeX (imported, not run) |
| `run_all.py` | — | runs `01 → 02 → 03` in order |

Reproduce everything from the repo root:

```bash
python code/run_all.py
```

Nothing here should print or paste numbers into the paper — scripts emit `.tex`
and `.pdf` files that `manuscript.tex` pulls in. See `CLAUDE.md` §8.
