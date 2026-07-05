"""Reproduce the entire analysis from data/raw/ in one command.

    python code/run_all.py

Runs the numbered stages in order. After it finishes, `git status` should be
clean: every tracked table and figure is regenerated identically from the raw
data (CLAUDE.md §9). This single entry point is what a reviewer re-runs to
verify the paper.
"""
from __future__ import annotations
import runpy
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
STAGES = ["01_build.py", "02_analyze.py", "03_figures.py"]


def main() -> None:
    for stage in STAGES:
        print(f"=== running {stage} ===")
        runpy.run_path(str(HERE / stage), run_name="__main__")
    print("=== done: tables/ and figures/ regenerated from data/raw/ ===")


if __name__ == "__main__":
    main()
