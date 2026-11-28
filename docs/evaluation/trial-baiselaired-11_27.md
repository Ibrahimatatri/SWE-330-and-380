# Clean-Setup Trial (GQM Q3, reproducibility)
This is a failed test. It utilized the git-installed bash shell, as doing this from either Windows-native terminal should fail.

## Machine
- Operating system and version: Windows 11 (26300.10075)
- CPU / RAM: AMD Ryzen 9 3900X / 32GB DDR4 RAM
- Python version: 3.13.7

## Steps

| # | What you did (exact command) | Minutes | Worked? | Notes (errors, guesses, missing docs) |
|---|---|---|---|---|
| 1 | `git clone https://github.com/Ibrahimatatri/SWE-330-and-380 && cd SWE-330-and-380` | 0 | Y | N/A |
| 2 | Download and check the release as in `data/README.md` | 60 or so | Y | N/A |
| 3 | `python3 -m venv .venv && source .venv/bin/activate && make setup` | 1 | N | There is no bin subdirectory to .venv |
| 4 | `make test` | 0 | N | bash: make: command not found |
| 5 | `make pipeline DB=/path/to/agent_skills_release.db` (optional: `make census DB=...`, about 25 minutes) | 0 | N | bash: make: command not found |
| 6 | `git status --short results/ figures/` (no changes = identical outputs) | 0 | N | No results directory, of course |

## Results (metrics M3.1–M3.5)
- Clean-setup success (yes/no): No
- Manual steps not covered by `make` (count and list): N/A
- Total minutes, excluding the dataset download: Maybe 10
- Row counts printed by the pipeline (hashes indexed, Skills sampled, findings): N/A
- Do `results/sprint2/*.csv` and the figure match the committed versions? (output of step 6): N/A
