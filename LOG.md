# LOG.md — Working Narrative

A dated, plain-language diary a coauthor can follow **without reading code**. One
bullet per meaningful step; newest date last. Reference commits and issues so a
reader can jump to the detail. This file answers *what happened, in order* (see
`CLAUDE.md` §6).

Template:

```
## YYYY-MM-DD
- <what I did and what I found, in plain words>. (commit <sha> / issue #N)
```

---

## 2026-07-06
- Set up the repository as a responsible AI-assisted research template: wrote the
  agent operating manual (`CLAUDE.md`), the README, the issue/PR templates, and
  the CI that compiles the paper. Pinned the Python environment in
  `requirements.txt`. Nothing analytical yet — this commit is the scaffold and
  the rules of the road.
- Built the analysis datasets from `pwt110.dta`: income per capita is
  `rgdpna/pop`; kept the 1960–2019 window and dropped PPP outliers and countries
  missing an endpoint. The estimation sample is **105 countries** (99 once the
  Solow controls are required); every dropped country is listed in
  `tables/attrition.tex`. Also built a 105-country balanced panel for the
  dispersion analysis. Choices logged as D-0001 and D-0002.
- Ran the absolute β-convergence regression (average annual growth on log initial
  GDP per capita) with robust SEs. The coefficient is small and **not
  significant** (β = −0.0017, p = 0.17, R² = 0.02) — no absolute convergence, the
  classic textbook result. Also computed σ-convergence: cross-country dispersion
  of log income actually **rose** from 1.02 (1960) to 1.21 (2019). Tables and
  in-text macros are emitted to `tables/`. Decisions D-0003 (estimation) and
  D-0004 (toolchain) logged.
- Made the two figures: the initial-income-vs-growth scatter (visibly flat,
  confirming no absolute convergence) and the σ-dispersion time series (rising).
  Saved as PDFs in `figures/`.
- Wrote the manuscript (Abstract, Introduction, Data, Methods, Results,
  Conclusions, References). Every number is pulled in via `\input{}` or an
  `estimates.tex` macro — nothing is typed by hand. Compiled it locally with
  latexmk: 4 pages, all citations resolve. The paper reports the honest null
  (no absolute β-convergence, σ-divergence) and flags conditional convergence as
  the next step.
- Reproducibility check caught a bug: re-running the pipeline changed the figure
  PDFs (matplotlib stamps a creation date), so `git status` was not clean. Fixed
  by stripping the PDF timestamp; figures are now byte-identical across runs.

## 2026-07-06 (issue #1 — conditional convergence)
- Per #1, added **conditional** β-convergence with the Solow controls (investment,
  population growth, human capital). The result flips: conditional β = −0.0131
  (p < 0.001, R² = 0.60), an implied convergence speed of ~2.5%/yr (half-life ~28
  years) — the classic Mankiw–Romer–Weil finding. Human capital is the strongest
  control. So the world *does* converge, but toward country-specific steady
  states, not a common one. Logged as D-0005.
- Period-sensitivity check (also #1): re-estimated on 1990–2019; the conditional
  speed is ~1.8%/yr — same story, slightly slower. Reassuring.
