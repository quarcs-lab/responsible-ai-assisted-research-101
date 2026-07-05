# `data/raw/` — immutable inputs

**Never edit or overwrite anything in this folder.** Raw data is the read-only
ground truth of the project. All cleaning happens in `code/` and lands in
`data/derived/` (which is git-ignored and rebuilt).

## `pwt110.dta`

- **What:** Penn World Table version 11.0 — a panel of national-accounts and
  PPP variables for ~180 economies, with real values in **2021 US$**.
- **Source:** Feenstra, Inklaar & Timmer (2015), *"The Next Generation of the
  Penn World Table"*, American Economic Review 105(10), 3150–3182.
  Download page: <https://www.rug.nl/ggdc/productivity/pwt/>
- **Why it is committed here:** it is small (~3.7 MB) and public, which makes
  this template clone-and-run. For your own project, prefer to keep large or
  private raw data *out* of git and document how to download it instead (this
  README is the place to do that).

Key variables used by the worked example: `countrycode`, `country`, `year`,
`rgdpna` (real GDP, constant 2021 national prices), `pop` (population, millions),
`emp` (persons engaged, millions), `csh_i` (investment share of GDP), `delta`
(depreciation rate), `hc` (human-capital index), `i_outlier` (PPP outlier flag).
