# Clean-Setup Trial (GQM Q3, reproducibility)

**Course:** SWE 330 · **When:** before the Phase 3 evaluation · **Who:** a member who did not write the pipeline (suggested: skyr-csc or ixmecrash)

Copy this file to `docs/evaluation/trial-<github-username>-<date>.md` and fill it in while you work. Do not ask the code authors for help during the trial; write down every place where you had to guess.

## Machine
- Operating system and version:
- CPU / RAM:
- Python version (`python3 --version`):

## Steps

| # | What you did (exact command) | Minutes | Worked? | Notes (errors, guesses, missing docs) |
|---|---|---|---|---|
| 1 | `git clone https://github.com/Ibrahimatatri/SWE-330-and-380 && cd SWE-330-and-380` | | | |
| 2 | Download and check the release as in `data/README.md` | | | |
| 3 | `make setup` | | | |
| 4 | `make test` | | | |
| 5 | `make pipeline DB=/path/to/agent_skills_release.db` | | | |
| 6 | `git status --short results/ figures/` (no changes = identical outputs) | | | |

## Results (metrics M3.1–M3.5)
- Clean-setup success (yes/no):
- Manual steps not covered by `make` (count and list):
- Total minutes, excluding the dataset download:
- Row counts printed by the pipeline (hashes indexed, Skills sampled, findings):
- Do `results/sprint2/*.csv` and the figure match the committed versions? (output of step 6):
