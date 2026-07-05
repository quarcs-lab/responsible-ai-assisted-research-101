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
