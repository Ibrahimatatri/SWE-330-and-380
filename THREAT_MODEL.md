# Threat Model and Capability Taxonomy

**Courses:** both (SWE 380 direction A.4 requires a threat model; the SWE 330 security decision depends on it). **Issue:** #5 · **Status:** Draft v0.1, 2026-10-07. Rules will be tuned after the annotation guide is written (#19).

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

## 3. Finding record

Every finding must contain: `category`, `rule_id`, `source_file`, `line` (and character span where available), `evidence` (a trimmed snippet), `explanation`, `review_level` (`info` / `review` / `high-review`), and `context` (one of `prose`, `code_fence`, `inline_code`, `front_matter`, `link`).

Categories are always reported separately. Any aggregate score is secondary and never replaces the per-category flags.

## 4. Context handling (known hard cases)

| Case | Planned handling | Error-taxonomy label |
|---|---|---|
| URL that is only a documentation link | `link` context gets a lower review level than an explicit fetch command | `doc-url` |
| Quoted example output | Lower level when the surrounding prose says "example" or "output" | `quoted-example` |
| Negated instruction ("never run `rm -rf`") | Negation cue near the match lowers the level, but the finding is still recorded | `negation` |
| Code fence without a language tag | Treated as possible commands | `code-fence` |
| Benign setup command | Reported as `INST` at `info` level | `benign-setup` |
| Ambiguous credential wording | `CRED` only when an action verb is present (read, print, send, export) | `ambiguous-cred` |
| Context lost while parsing | Counted per run, reviewed in the error analysis | `parse-context` |

## 5. What SkillGuard does not establish

A finding does not show maliciousness, execution, harm, exploitability, or author intent. Absence of findings does not show that a Skill is safe.
