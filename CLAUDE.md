# CLAUDE.md — Operating Manual for AI-Assisted Work in This Repository

This file governs how any AI agent (and any human) works in this repository.
**Read it fully before touching anything.** It is loaded automatically by Claude
Code at the start of every session; other agents should be pointed at it first.

> **Prime directive.** AI has collapsed the cost of *doing* research work —
> coding, cleaning data, running analyses — but *not* the cost of *verifying*
> that the work is correct. The gap between the two is **verification debt**.
> Everything in this repo exists to keep verification *cheaper than the work*:
> leave a trail a human can check in small, bounded pieces. And remember —
> **a computer can never be held accountable. A named human signs every merge.**

This workflow operationalizes the practices in Paul Goldsmith-Pinkham,
*"Integration and Collaboration in AI Research Work"*
(https://paulgp.substack.com/p/integration-and-collaboration-in).

---

## 1. Project overview & the research task

- **Goal:** a reproducible empirical study of **Solow growth convergence** using
  the Penn World Table 11.0 (`data/raw/pwt110.dta`, real values in 2021 US$).
- **Question:** do initially poorer economies grow faster and catch up
  (*absolute* β-convergence)? Does catch-up hold once we condition on the Solow
  determinants of the steady state — investment, population growth, human
  capital (*conditional* β-convergence)? Is cross-country dispersion of income
  shrinking over time (*σ-convergence*)?
- **Deliverable:** `manuscript.tex` → PDF, where **every number, table, and
  figure is emitted by code** in `code/`. Nothing is typed by hand.
- **The pipeline (memorize this):**

  ```
  data/raw/pwt110.dta
        │  code/01_build.py
        ▼
  data/derived/*.parquet ──► tables/*.tex + figures/*.pdf
        │  02_analyze.py, 03_figures.py    │ \input{} / \includegraphics{}
        ▼                                  ▼
  (rebuildable, git-ignored)         manuscript.tex ──CI──► PDF ──► Overleaf
  ```

> **Reusing this template for your own project?** Rewrite this section to your
> question and data, replace the `code/` scripts and `data/raw/` file, and reset
> `DECISIONS.md` / `LOG.md`. Keep everything from §2 onward unchanged — those
> rules are project-agnostic.

---

## 2. The five golden rules

1. **Ask for the trail before the work.** Every task begins with a short plan
   that states *how the result will be verifiable* — which script runs, which
   output file it writes, and what a human should re-run to confirm it. No plan,
   no code.
2. **Ship reviewable commits, not code dumps.** One logical step per commit. A
   human reviews the *diff*, never the whole codebase. If a change cannot be
   read in a few minutes, split it.
3. **`DECISIONS.md` / `LOG.md` are a map, not a verdict.** They tell a human
   *where to look* and *what to re-run*. You may be wrong, or may have skipped a
   step. **Never record work as done that you did not actually run and observe.**
4. **Route all feedback through GitHub Issues.** Titled, permanent, indexed.
   Reference issues from commits and logs with `#N`. Resolve them on a branch
   via a Pull Request — never by silently editing `main`.
5. **No number in the draft is typed by hand.** Code emits `tables/*.tex` and
   `figures/*.pdf`; the manuscript `\input{}`s / `\includegraphics{}`s them; git
   connects the two. If a number in the PDF cannot be traced to a script output,
   it is a bug.

---

## 3. Repository map

| Path | Purpose |
|------|---------|
| `code/` | Analysis scripts, numbered in run order. `run_all.py` reproduces everything. |
| `data/raw/` | Immutable inputs (`pwt110.dta`). **Never edit or overwrite.** |
| `data/derived/` | Machine-built intermediates. Git-ignored; rebuilt by code. |
| `tables/` | Code-emitted `.tex` tables + `estimates.tex` (in-text macros). Committed. |
| `figures/` | Code-emitted `.pdf` figures. Committed. |
| `manuscript.tex` | The paper. Only `\input{}` / `\includegraphics{}` for every number. |
| `references.bib` | Bibliography. |
| `DECISIONS.md` | Methodological choices: rationale, alternatives, confidence, trail. |
| `LOG.md` | Plain-language dated narrative a coauthor can follow. |
| `.github/` | Issue form, PR template, and CI that compiles the PDF. |

---

## 4. How to start any piece of work (plan first)

Before writing code, respond with three things and wait for confirmation on
anything non-trivial:

1. **What** you will do — one logical step.
2. **How it will be verified** — the exact script/output/check that proves it,
   and what a human should re-run to confirm (rule #1).
3. **Which files** you will touch.

Then implement *that step only*. Smaller chunks are more reliable and far easier
to verify than one big autonomous run.

---

## 5. Commit discipline

- **When:** commit when one logical step is complete and self-consistent — the
  script runs and its outputs regenerate. Commit *per step*, not "end of
  session."
- **One logical step per commit.** Never mix data-building, analysis, and prose
  in the same commit.
- **Regenerate outputs in the same commit as the code that produces them,** so
  `tables/` and `figures/` never drift from `code/`.
- **Message format:**

  ```
  <type>: <what changed> (<why, in a few words>)

  <body: what changed, why this way, and how you verified it —
   e.g. "re-ran run_all.py; convergence table regenerated, betaAbs unchanged">

  Refs #<issue>        (or "Closes #<issue>")
  ```

  Types: `data`, `analysis`, `table`, `figure`, `paper`, `docs`, `chore`, `fix`.
  The body **must** explain *why* and **state the verification you actually ran**.

- Never commit secrets, anything under `data/derived/`, or LaTeX build junk
  (see `.gitignore`).

---

## 6. `DECISIONS.md` vs `LOG.md` — what goes where

- **`DECISIONS.md` = *why the analysis is the way it is.*** Append an entry
  whenever you make a methodological choice that has a defensible alternative
  (sample, variable construction, estimator, controls, a cleaning rule). Record
  the rejected alternatives, the rationale, a **confidence level**, and links to
  the commit/issue/script. If a later decision supersedes an earlier one, add a
  new entry and mark the old one *Superseded* — never rewrite history.
- **`LOG.md` = *what happened, in order, in plain language.*** Append a dated
  bullet after each meaningful step so a coauthor can follow the story without
  reading code. Narrative, not justification.
- **Rule of thumb:** a *choice with alternatives* → `DECISIONS.md`; an *event* →
  `LOG.md`. Most substantive steps touch both. Both are a map to verify, never
  proof that the work is correct.

---

## 7. The issue-driven loop

All feedback, bugs, and validation/robustness requests become GitHub Issues.
For each issue:

1. **Read** the issue; restate its acceptance criteria and the trail it asks for.
2. `git switch -c issue-<N>-<slug>` — work on a branch.
3. Implement in reviewable commits, each referencing `Refs #<N>`.
4. Update `DECISIONS.md` / `LOG.md` as needed.
5. Push; open a PR that fills `.github/PULL_REQUEST_TEMPLATE.md` and says
   `Closes #<N>`.
6. A **human** reviews the diff and merges. The merge closes the issue and CI
   rebuilds the PDF.

Use the `gh` CLI for all of this (`gh issue view`, `gh pr create`, `gh pr merge`).

---

## 8. No hand-typed numbers — wiring results into the paper

- **Regression tables:** code writes `tables/<name>.tex` (a booktabs `tabular`);
  the manuscript does `\input{tables/<name>.tex}`.
- **In-text numbers** (a coefficient, an `N`, an `R²`, a convergence rate): code
  writes LaTeX macros into `tables/estimates.tex`, e.g.
  `\newcommand{\betaCond}{-0.018}`; the prose uses `\betaCond`. **Never paste a
  number into a sentence.**
- **Figures:** code writes `figures/<name>.pdf`; the manuscript does
  `\includegraphics{figures/<name>.pdf}`.
- **Method before plumbing.** Verify the *analysis* is right before wiring its
  results into the draft. Clean provenance can faithfully publish a wrong
  estimate.

---

## 9. The human verification checklist (run before merging)

A **human** runs this — the agent cannot self-certify.

- [ ] `python code/run_all.py` reproduces every `tables/*.tex` and
      `figures/*.pdf` from `data/raw/` with no manual steps.
- [ ] `git status` is clean after the run (committed outputs == regenerated).
- [ ] Spot-check 2–3 numbers in the compiled PDF — each traces to a script
      output or an `estimates.tex` macro.
- [ ] The commits match what `DECISIONS.md` / `LOG.md` claim was done.
- [ ] The diff is bounded; each commit is one logical step.
- [ ] CI (`build-manuscript`) is green and the PDF artifact opens.

---

## 10. Security & data rules

- Never commit credentials, tokens, or `.env` files; never print secrets to a
  log. See `.gitignore`.
- `data/raw/` is read-only truth; **never edit `pwt110.dta`**.
- `data/derived/` is rebuildable → git-ignored. Do not commit it.
- Do not add large binaries beyond the committed dataset. Keep large or private
  raw data *out* of git and document how to fetch it (`data/raw/README.md`).

---

## 11. Environment / how to run

- Python 3.11–3.14. Dependencies pinned in `requirements.txt`.
- Set up:  `uv venv && uv pip install -r requirements.txt`
  (or `python -m venv .venv && .venv/bin/pip install -r requirements.txt`).
- Reproduce everything:  `python code/run_all.py`
- Compile the paper locally:  `latexmk -pdf manuscript.tex`
- Never hand-edit anything under `data/derived/`, `tables/`, or `figures/` —
  those are generated.

---

## 12. Never do

- **NEVER** type a number into `manuscript.tex` by hand.
- **NEVER** claim you ran or verified something you did not actually execute.
- **NEVER** invent, fabricate, hand-fill, or "impute for convenience" a data value.
- **NEVER** edit files under `data/raw/`.
- **NEVER** force-push or rewrite shared history (`main` or any pushed branch).
- **NEVER** resolve feedback by editing `main` directly — use an issue + a PR.
- **NEVER** commit secrets or anything under `data/derived/`.
