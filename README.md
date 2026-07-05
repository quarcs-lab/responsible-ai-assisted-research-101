# Responsible AI-Assisted Empirical Research 101

A **template repository** for doing empirical research *with* AI coding agents
without drowning in **verification debt**. It pairs a working scaffold with an
operating manual (`CLAUDE.md`) and demonstrates the entire workflow end-to-end on
a short but real example: **Solow growth convergence on Penn World Table 11.0
data.**

Clone it, replace the example with your own study, and you inherit a rigorous,
reproducible, human-accountable workflow that wires **agentic coding → Git →
GitHub → Overleaf** together.

> This template operationalizes the ideas in Paul Goldsmith-Pinkham,
> [*"Integration and Collaboration in AI Research Work"*](https://paulgp.substack.com/p/integration-and-collaboration-in).

---

## Why this exists

AI has collapsed the cost of *doing* research work — writing code, cleaning
data, running analyses. It has **not** collapsed the cost of *verifying* that the
work is correct. That gap is **verification debt**: a growing pile of
AI-produced results nobody has actually checked. Left unmanaged, it is how a
plausible-but-wrong number ends up in a published paper.

The cure is borrowed from software engineering, distilled into **five
practices** that this repo builds in by default:

1. **Ask for the trail before the work** — put the verifiability requirements in
   the prompt / issue, up front.
2. **Review commits, not codebases** — verify bounded, one-step diffs.
3. **Treat `DECISIONS.md` / `LOG.md` as a map to verify, not a verdict** — LLMs
   happily claim work they did not do; a human checks.
4. **Route feedback through GitHub Issues** (and Pull Requests) — titled,
   permanent, indexed.
5. **No number in the draft is typed by hand** — code emits the tables and
   figures; the paper `\input{}`s them; git connects them.

And one non-negotiable: **a computer can never be held accountable — a named
human signs every merge.**

---

## The research task *you* describe

The example question is Solow convergence, but **the template is generic**. To
make it yours, you write your own research task — the cleanest place is a GitHub
Issue using the built-in *Research task* form. State four things:

1. **The question** — what you want to know.
2. **The data** — what is in `data/raw/`.
3. **The output** — the table(s) / figure(s) that would answer it.
4. **How the result should be verifiable** — the trail to leave (which script,
   which output file, which number).

Everything downstream keys off that description. (See *How to adapt this
template* at the bottom.)

---

## How the template works, end to end

Every arrow below is git-tracked, so a change at any stage produces a **bounded,
reviewable diff** — and the paper is always exactly one command away from its
data.

```
 data/raw/pwt110.dta
       │  code/01_build.py
       ▼
 data/derived/*.parquet ─────► tables/*.tex  +  figures/*.pdf
       │  02_analyze.py               │  \input{} / \includegraphics{}
       │  03_figures.py               ▼
 (git-ignored, rebuilt)         manuscript.tex ──► GitHub Actions ──► PDF
                                      │  git sync
                                      ▼
                                   Overleaf  (write prose; numbers stay code-driven)
```

- **The agent** works under the rules in `CLAUDE.md`.
- **Git** records one logical step per commit, with a message that says *why*.
- **GitHub** carries the feedback loop (Issues) and the review gate (Pull
  Requests), and **CI compiles the paper** on every change.
- **Overleaf** is where humans write prose, synced to the same GitHub repo so
  numbers only ever enter through code-emitted files.

---

## How agentic coding integrates with Git, GitHub, and Overleaf

| Layer | What it does here | Where it's configured |
|-------|-------------------|-----------------------|
| **AI agent** (Claude Code, etc.) | Plans, writes code, commits, opens issues/PRs — but leaves a checkable trail | `CLAUDE.md` |
| **Git** | One logical step per commit; outputs regenerate in the same commit as their code | `CLAUDE.md` §5 |
| **GitHub — Issues** | Every task / bug / validation request is a titled, permanent record referenced with `#N` | `.github/ISSUE_TEMPLATE/` |
| **GitHub — Pull Requests** | The human review gate; each PR carries a verification checklist and a named reviewer | `.github/PULL_REQUEST_TEMPLATE.md` |
| **GitHub — Actions (CI)** | Compiles `manuscript.tex` → PDF on every change; a green check means the paper builds from what's committed | `.github/workflows/build-manuscript.yml` |
| **Overleaf** | Collaborative prose writing, GitHub-synced; the "no hand-typed numbers" rule survives the round trip | *Overleaf ↔ GitHub sync*, below |

---

## The three governance files: `CLAUDE.md`, `DECISIONS.md`, `LOG.md`

They answer three different questions and change at three different rates. Do not
collapse them into one.

| File | Answers | Audience | Changes |
|------|---------|----------|---------|
| **`CLAUDE.md`** | *How do we work here?* (the rules) | the agent + you | rarely — only when the process changes |
| **`DECISIONS.md`** | *Why is the analysis the way it is?* (choices, alternatives, **confidence**) | reviewers, coauthors, your future self | on each methodological choice |
| **`LOG.md`** | *What happened, in order?* (plain-language narrative) | coauthors | after each meaningful step |

- `CLAUDE.md` is the **contract** the agent works under — the five golden rules,
  commit discipline, the issue loop, the no-hand-typed-numbers wiring, and the
  human verification checklist.
- `DECISIONS.md` is the **methodological ledger**. Each entry records the choice,
  the alternatives rejected, the rationale, a confidence level, and a trail
  (commit / issue / PR / script). It is a *map to verify*, not proof the choice
  was right.
- `LOG.md` is the **diary**. A coauthor should be able to follow the whole story
  from it without reading a line of code.

---

## Folder structure

```
responsible-ai-assisted-research-101/
├── README.md              ← you are here: how the template works
├── CLAUDE.md              ← agent operating manual (the five practices)
├── DECISIONS.md           ← methodological choices: rationale, alternatives, confidence, trail
├── LOG.md                 ← plain-language dated narrative for coauthors
├── manuscript.tex         ← the paper; \input{}s numbers, never hand-typed
├── references.bib         ← bibliography
├── requirements.txt       ← pinned Python dependencies
├── code/                  ← analysis scripts, numbered in run order; run_all.py reproduces all
│   ├── config.py          ← paths + parameters (edit to reconfigure)
│   ├── 01_build.py        ← raw .dta → derived data + attrition table
│   ├── 02_analyze.py      ← regressions, σ-series → tables/*.tex, estimates.tex
│   ├── 03_figures.py      ← figures → figures/*.pdf
│   ├── latexout.py        ← helper: emit LaTeX macros/tables
│   └── run_all.py         ← runs 01 → 02 → 03
├── data/
│   ├── raw/               ← immutable inputs — pwt110.dta (PWT 11.0); never edited
│   └── derived/           ← machine-built intermediates; git-ignored, rebuilt by code
├── tables/                ← code-emitted .tex tables + estimates.tex (in-text macros)
├── figures/               ← code-emitted .pdf figures
└── .github/               ← issue form, PR template, CI (build-manuscript)
```

---

## How to use this template

1. **Create your copy.** Click **"Use this template" → Create a new repository**
   on GitHub, then clone your copy.
2. **Set up the environment.**
   `uv venv && uv pip install -r requirements.txt`
   (or `python -m venv .venv && .venv/bin/pip install -r requirements.txt`).
3. **Describe your task in a GitHub Issue** using the *Research task* form —
   include the verifiability requirements (the trail to leave).
4. **Point your AI agent at the repo.** It reads `CLAUDE.md`, makes a short plan,
   then works the issue **on a branch in reviewable commits**.
5. **Review the commits, not the codebase.** Read each diff; check that
   `LOG.md` / `DECISIONS.md` match what the commits actually did.
6. **File follow-up issues** for anything to validate, fix, or extend; reference
   them with `#N`.
7. **Generate results.** Code emits `tables/*.tex` and `figures/*.pdf`; confirm
   with `python code/run_all.py` — `git status` must be clean afterward.
8. **Write the paper** in `manuscript.tex` using `\input{}` and the macros in
   `tables/estimates.tex` — never type a number.
9. **Open a Pull Request,** run the verification checklist, and have a **human**
   merge it. CI compiles the PDF artifact.
10. **Deploy to Overleaf** via GitHub sync (below).

---

## Overleaf ↔ GitHub sync setup

Overleaf's GitHub integration keeps this repo and your Overleaf project in sync.
It is a premium Overleaf feature, but **only the project owner needs the
subscription**. Sync is **documented here, not automated** — you push/pull
deliberately.

1. In Overleaf: **New Project → Import from GitHub**, and select your copy of
   this repo. `manuscript.tex` becomes the Overleaf main document.
2. **Write prose in Overleaf.** It edits the same `manuscript.tex`.
3. **Pull code-generated results:** after the agent pushes new `tables/*.tex` or
   `figures/*.pdf`, in Overleaf go to **Menu → GitHub → Pull GitHub changes**.
4. **Push prose edits back:** **Menu → GitHub → Push Overleaf changes to
   GitHub.** Your commits appear on GitHub and trigger the `build-manuscript` CI.

The golden rule survives the round trip: numbers only enter the paper via
`\input{}` of code-emitted files, so Overleaf edits can never introduce a
hand-typed value.

---

## The worked example (what ships in this repo)

A complete, short study of **Solow convergence** you can read as a reference:

- **Absolute β-convergence** — do poorer countries grow faster, unconditionally?
- **Conditional β-convergence** — does catch-up appear once we condition on the
  Solow steady-state determinants (investment, population growth, human capital)?
- **σ-convergence** — is the cross-country dispersion of income shrinking?

The git history is itself a teaching artifact: a clean initial pipeline on
`main`, then a validation **Issue**, resolved on a branch via a reviewed
**Pull Request** — the exact issue-driven loop from the blog post. Read the
commit log, `DECISIONS.md`, and the closed issue/PR to see the workflow in
motion.

---

## How to adapt this template for your own project

1. Replace `data/raw/pwt110.dta` with your data and update `data/raw/README.md`.
2. Rewrite `code/01_build.py … 03_figures.py` for your pipeline, keeping
   `run_all.py` as the single entry point that regenerates `tables/` and
   `figures/`.
3. Reset `DECISIONS.md` and `LOG.md` — keep the templates at the top, delete the
   Solow entries.
4. Edit `CLAUDE.md` §1 (*Project overview*) to your question; **keep §§2–12
   unchanged** — those rules are project-agnostic.
5. Rewrite `manuscript.tex` and `references.bib`, keeping the `\input{}` / macro
   discipline (no hand-typed numbers).
6. Keep `.github/` as-is — the issue form, PR checklist, and CI are
   project-agnostic.

---

## License

Code is released under the [MIT License](LICENSE). If you build a paper from this
template, consider licensing the written content (CC BY 4.0) separately; the Penn
World Table data is redistributed under its own terms (see `data/raw/README.md`).
