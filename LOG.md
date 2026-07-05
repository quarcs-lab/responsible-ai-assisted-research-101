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
