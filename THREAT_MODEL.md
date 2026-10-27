# Threat Model and Capability Taxonomy

**Courses:** both (SWE 380 direction A.4 requires a threat model; the SWE 330 security decision depends on it). **Issue:** #5 · **Status:** v0.2, 2026-10-26. Rules are implemented in `src/skillguard/detectors/` and will be tuned after manual validation (#19).

## 1. What we are protecting against

SkillGuard models two separate concerns.

### A. Risks *described by* Skills (what we detect)
A Skill is a set of instructions that an AI agent follows with the permissions of the user who installed it. A Skill copied from another repository may tell the agent to do things the adopting developer did not notice.

| Asset | Threat | Example signal |
|---|---|---|
| User's machine and shell | Agent runs arbitrary or destructive commands | `rm -rf`, `sudo`, `curl … \| sh` |
| Source code and files | Agent reads or modifies files outside the task's needs | Writes to `~/.ssh`, broad `find /` |
| Credentials and secrets | Agent reads, prints, or sends secrets | `cat .env`, `$AWS_SECRET_ACCESS_KEY` |
| Network boundary | Agent contacts external endpoints or exfiltrates data | `curl -X POST https://…`, `wget` |
| Software supply chain | Agent installs unpinned or unknown packages | `pip install`, `npm i -g`, `brew install` |
| Bundled code | Agent runs scripts shipped with the Skill without review | `python scripts/setup.py`, `bash ./run.sh` |

**Actors considered:** a careless or over-broad Skill author (most likely); a Skill that was benign originally but altered in a copy; a deliberately malicious author (possible but **never asserted** by SkillGuard).

### B. Risks *to the team* from handling the dataset (how we stay safe)
The pipeline only reads text, so these are design constraints more than likely threats: the controls keep it that way and make it checkable in tests.

| Threat | Control |
|---|---|
| Accidentally executing dataset content | Content is only ever a Python `str`. No `subprocess`, `os.system`, `eval`, `exec`, `importlib`, network clients, or installers on any data path. A test asserts this (issue #10). |
| Following URLs in the data | URLs are parsed as text only and never fetched |
| Leaking personal data | No author identities in reports. Aggregate results, with minimal evidence snippets. Repository names only where needed for traceability. |
| Committing the dataset | `.gitignore` covers `data/raw/`, database and Parquet files. Only small hand-written fixtures are committed. |
| Malicious file content (e.g., huge files, odd encodings) | Read with size limits and `errors="replace"`. Malformed records are skipped and counted, not crashed on. |

## 2. Capability taxonomy (v0.1)

| ID | Category | What counts | Common benign cases (false-positive risks) |
|---|---|---|---|
| `CMD` | Command execution | Instructions to run shell, terminal, or interpreter commands; fenced `bash`/`sh` blocks presented as steps | Example output, prose that names a command without asking for it to be run |
| `NET` | Network access | Instructions to fetch, POST, or download; `curl`/`wget`/HTTP-client usage; API calls | Documentation links, citation URLs, badges |
| `FS` | File-system access | Instructions to read, write, move, or delete files beyond the Skill's own folder; broad globs | Reading the project's own files is normal for coding Skills |
| `CRED` | Credential or secret access | Reading, printing, or sending tokens, keys, `.env` files, keychains, SSH keys | Advice to *never* commit secrets; mentioning "API key" in setup notes |
| `INST` | Dependency installation or system modification | `pip`/`npm`/`brew`/`apt` installs; editing shell profiles; changing system configuration | Normal one-time setup steps |
| `SCRIPT` | Bundled-script execution | Running scripts shipped in the Skill's folder | A script that is present but never invoked |
| `PRIV` | Destructive or privileged operations | `sudo`, `chmod 777`, `rm -rf`, force-push, disk or database drops | Warnings that say "do not run X" |

Each rule has a stable ID of the form `<CATEGORY>-<NNN>` (for example, `NET-001`). Rule IDs are never reused once published.

**Implemented in v0.2 (23 rules):** CMD-001–004, NET-001–004, FS-001–005, CRED-001–004, INST-001–004, SCRIPT-001–002. Each rule's pattern, contexts, and explanation are in `src/skillguard/detectors/<category>.py`, and each has a positive and a negative test. `PRIV` is held out on purpose: adding it later is the SWE 330 extensibility experiment (GQM Q1).

**Bundled executables:** `SCRIPT-001` tags every instruction to run a script file (for example `python scripts/x.py` or `./run.sh`), and the release's `has_scripts` flag records which Skill folders ship scripts at all.

## 3. Finding record

Every finding contains: `category`, `rule_id`, `line`, `evidence` (at most 160 characters, secrets masked), `explanation`, `review_level` (`info` / `review` / `high`), `context` (`front_matter`, `prose`, or `code:<language>`), and `source` (repository/path). Only `review` and `high` findings count toward the research outcomes; `info` findings are kept for transparency. On the Sprint 2 sample, 100% of 207,645 findings carried every field.

Categories are always reported separately. Any aggregate score is secondary and never replaces the per-category flags.

## 4. Context handling (known hard cases)

| Case | Handling in v0.2 | Error-taxonomy label |
|---|---|---|
| URL that is only a documentation link | URLs in prose are `NET-002` at `info` (never counted); URLs in shell code are `NET-003` at `review` | `doc-url` |
| Quoted example output | Not handled yet; tracked in validation | `quoted-example` |
| Negated instruction ("never run `rm -rf`") | In prose, a cue (never, do not, avoid, ...) within 40 characters before the match lowers it to `info`; the finding is still recorded | `negation` |
| Code fence without a language tag | Only prompt-style lines (`$ cmd`) count as commands (`CMD-002`); other untagged lines do not | `code-fence` |
| Benign setup command | Currently counted as `INST` at `review`; to be reconsidered after validation | `benign-setup` |
| Ambiguous credential wording | `CRED-003` needs an action verb (read, print, send, copy, log, ...) near the credential word | `ambiguous-cred` |
| Context lost while parsing | Not measured yet; reviewed in the error analysis | `parse-context` |

## 5. What SkillGuard does not establish

A finding does not show maliciousness, execution, harm, exploitability, or author intent. Absence of findings does not show that a Skill is safe.
