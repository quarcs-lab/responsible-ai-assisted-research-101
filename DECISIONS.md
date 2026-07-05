# DECISIONS.md — Methodological Decision Log

Append **one entry per methodological choice that has a defensible alternative**
(sample, variable construction, estimator, controls, a cleaning rule). This file
answers *why the analysis is the way it is*. It is a **map for a human to
verify**, not proof that a choice is correct (see `CLAUDE.md` §6).

Newest entries at the bottom. **Never rewrite history** — if a later decision
overturns an earlier one, add a new entry and mark the old one *Superseded*.

---

## Entry template (copy this)

```text
## D-000N: <short title of the decision>

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by D-000M
- **Decision:** <what was chosen, in one sentence>
- **Context / question:** <the fork in the road this resolves>
- **Alternatives rejected:**
  - <alternative A> — <why not>
  - <alternative B> — <why not>
- **Rationale:** <why this choice, given the question>
- **Confidence:** High | Medium | Low — <what evidence would change it>
- **Trail:** commit <sha>, issue #<N>, PR #<M>, script `code/<file>.py`
```

---

<!-- Decisions are appended below as the analysis develops. -->

## D-0001: Measure income as real GDP per capita, `rgdpna / pop`

- **Date:** 2026-07-06
- **Status:** Accepted
- **Decision:** Use PWT 11.0 `rgdpna` (real GDP at constant 2021 national prices)
  divided by `pop` as the income-per-capita variable, for both the initial level
  and the growth endpoints.
- **Context / question:** PWT offers several real-GDP concepts; convergence needs
  one series used consistently for the initial *level* and for *growth*.
- **Alternatives rejected:**
  - `rgdpe / pop` (expenditure-side, chained PPP) — best for cross-country
    *level* comparison, but PWT recommends the national-accounts series for
    growth *over time*; kept as a robustness option.
  - `rgdpo / emp` (output per worker) — closest to the Solow production function,
    but `emp` is missing for many countries and shrinks the sample.
- **Rationale:** `rgdpna` is PWT's recommended series for growth comparisons over
  time; per-capita (vs. per-worker) keeps country coverage broad. Exposed as the
  `INCOME_MEASURE` switch in `code/config.py` so alternatives are one edit away.
- **Confidence:** Medium — the qualitative convergence findings are robust to the
  measure; point estimates would shift somewhat under `rgdpe` or per-worker.
- **Trail:** `code/config.py` (`INCOME_MEASURE`), `code/01_build.py` (this commit).

## D-0002: Growth window 1960–2019; drop PPP outliers at the endpoints

- **Date:** 2026-07-06
- **Status:** Accepted
- **Decision:** Study the window 1960–2019, and drop a country if it is flagged
  `i_outlier == "Outlier"` in 1960 or 2019, or lacks positive GDP p.c. at either
  endpoint.
- **Context / question:** Which years bound the growth window, and which
  observations are reliable enough for a level-based convergence comparison?
- **Alternatives rejected:**
  - End in 2023 (latest data) — the 2020–23 COVID collapse contaminates the
    growth endpoint; noted as a robustness check instead.
  - Keep PPP outliers — PWT flags them precisely because their price-level
    comparison is unreliable, which distorts a level-based convergence test.
- **Rationale:** 1960 is the canonical Barro/MRW start with broad developing-
  country coverage; 2019 gives a long horizon that ends before COVID. Every
  dropped country is accounted for in `tables/attrition.tex`.
- **Confidence:** High — endpoints and the outlier rule are transparent and the
  attrition table lets a reviewer re-derive the sample exactly.
- **Trail:** `code/config.py` (`START_YEAR`, `END_YEAR`, `DROP_OUTLIERS`),
  `code/01_build.py`, `tables/attrition.tex` (this commit).

## D-0003: Estimate by OLS with robust SEs; derive λ from β (not λ = −β)

- **Date:** 2026-07-06
- **Status:** Accepted
- **Decision:** Estimate absolute β-convergence, g_i = α + β·y_{i,1960} + ε_i, by
  OLS with heteroskedasticity-robust (HC1) standard errors, and compute the
  implied convergence speed as λ = −ln(1 + βT)/T with half-life ln2/λ.
- **Context / question:** How to estimate the convergence regression and how to
  translate the slope β into an interpretable speed.
- **Alternatives rejected:**
  - Classical (homoskedastic) SEs — cross-country growth variances differ
    markedly; HC1 is the safer default.
  - The shortcut λ = −β — only a first-order approximation; it is wrong for the
    long horizon here (T = 59) and overstates the speed.
- **Rationale:** HC1 is standard for cross-country regressions; the exact
  Solow-linearization formula for λ is correct and guards the domain (defined
  only when 1 + βT > 0, i.e. when there is convergence).
- **Confidence:** High — textbook specification; the λ formula is derived in the
  Methods section of the manuscript.
- **Trail:** `code/02_analyze.py` (`implied_lambda`), `tables/convergence_regressions.tex`.

## D-0004: Emit results with statsmodels + a small in-repo LaTeX helper

- **Date:** 2026-07-06
- **Status:** Accepted
- **Decision:** Fit models with `statsmodels` and turn them into LaTeX with a
  ~120-line helper (`code/latexout.py`) rather than a dedicated table package.
- **Context / question:** How to satisfy the "no hand-typed numbers" rule —
  regression tables and in-text numbers must be code-emitted LaTeX.
- **Alternatives rejected:**
  - `stargazer` — lightly maintained; cannot easily add the implied-λ/half-life
    rows we want, and adds a dependency prone to API drift.
  - `pyfixest` (`etable`) — elegant, but pulls in `numba` and is sensitive to the
    Python version, which hurts install robustness for students.
- **Rationale:** The custom helper has zero heavy dependencies, installs anywhere,
  gives full control over the table (stars, robust SEs, λ/half-life rows), and is
  transparent — a reader sees exactly how a number becomes LaTeX.
- **Confidence:** High — the whole pipeline runs on a minimal, pinned stack.
- **Trail:** `code/latexout.py`, `requirements.txt`.

## D-0005: Conditional convergence controls = investment, population growth, human capital

- **Date:** 2026-07-06
- **Status:** Accepted
- **Decision:** Condition on the augmented-Solow determinants of the steady state,
  entered as in Mankiw–Romer–Weil (1992): ln(investment share `csh_i`),
  ln(`n + g + δ`) with population growth `n` from `pop`, assumed `g = 0.02`, and
  depreciation `δ` from PWT `delta`; and ln(human capital `hc`).
- **Context / question:** The absolute null (D-0003) does not test the Solow
  prediction, which is convergence to each economy's *own* steady state. Issue #1
  asks for the conditional test; which controls?
- **Alternatives rejected:**
  - No human capital (textbook Solow) — MRW show human capital is decisive; our
    data agree (its coefficient is large and highly significant).
  - Adding institutions/geography — moves beyond the Solow model this exercise
    tests, and invites endogeneity debates outside the scope of the example.
- **Rationale:** These are exactly the augmented-Solow steady-state determinants;
  using them keeps the test faithful to the theory and comparable to MRW.
- **Confidence:** High — conditional β is negative and significant (≈2.5%/yr),
  stable in the 1990–2019 subwindow; the qualitative result is robust.
- **Trail:** issue #1, `code/02_analyze.py` (`COND_FORMULA`),
  `tables/convergence_regressions.tex`, PR #2.
