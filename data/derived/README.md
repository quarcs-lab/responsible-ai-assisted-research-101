# `data/derived/` — machine-built intermediates

Everything here is **generated** by `code/` and **git-ignored** (see the root
`.gitignore`). Do not edit these files and do not commit them — they are rebuilt
from `data/raw/` every time you run:

```bash
python code/run_all.py
```

This folder is intentionally kept in git only via this README, so the directory
exists on a fresh clone before the pipeline runs. Expected contents after a run:
`cross_section.parquet`, `panel_balanced.parquet`, `sigma_series.csv`.
