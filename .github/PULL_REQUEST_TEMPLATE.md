<!--
A pull request is where a bounded, reviewable diff meets a human sign-off.
Keep the diff small (one issue's worth of logical steps). Fill every box
honestly — an unchecked box is information, not a failure.
-->

## What this PR does
<!-- One paragraph: the WHY, not just the WHAT. -->

Closes #<issue-number>

## Commits in this PR
<!-- One line per logical step, so a reviewer can walk the story. -->
-

## Verification checklist (the five practices)
- [ ] **Trail-first** — the linked issue stated *how* this would be verified, and this PR delivers exactly that trail.
- [ ] **Reviewable diff** — each commit is one logical step; the whole diff can be read in a few minutes.
- [ ] **Honest map** — `DECISIONS.md` / `LOG.md` match what the commits actually do; nothing is claimed that was not actually run.
- [ ] **Issue-driven** — this resolves a titled issue and references it with `#`.
- [ ] **No hand-typed numbers** — every new number in the paper comes from `tables/*.tex`, `tables/estimates.tex`, or `figures/*.pdf`; none was typed into prose.

## Reproducibility
- [ ] `python code/run_all.py` regenerates all outputs from `data/raw/`, and `git status` is clean afterward.
- [ ] CI (`build-manuscript`) is green and the `manuscript-pdf` artifact opens.

## Reviewer sign-off
<!-- A named human — not the agent — approves the merge. A computer cannot be held accountable. -->
Reviewer: @<github-handle>
