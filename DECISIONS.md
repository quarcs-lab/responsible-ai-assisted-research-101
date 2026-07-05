# DECISIONS.md — Methodological Decision Log

Append **one entry per methodological choice that has a defensible alternative**
(sample, variable construction, estimator, controls, a cleaning rule). This file
answers *why the analysis is the way it is*. It is a **map for a human to
verify**, not proof that a choice is correct (see `CLAUDE.md` §6).

Newest entries at the bottom. **Never rewrite history** — if a later decision
overturns an earlier one, add a new entry and mark the old one *Superseded*.

---

### Entry template (copy this)

```
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
