# Threat Model and Capability Taxonomy

**Courses:** both (SWE 380 direction A.4 requires a threat model; the SWE 330 security decision depends on it). **Issue:** #5 · **Status:** v1.0, 2026-11-16. Rules are implemented in `src/skillguard/detectors/`; precision and recall are measured by manual validation (#19).

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

## 2. Capability taxonomy (v1.0)

| ID | Category | What counts | Common benign cases (false-positive risks) |
|---|---|---|---|
| `CMD` | Command execution | Instructions to run shell, terminal, or interpreter commands; fenced `bash`/`sh` blocks presented as steps | Example output, prose that names a command without asking for it to be run |
| `NET` | Network access | Instructions to fetch, POST, or download; `curl`/`wget`/HTTP-client usage; API calls | Documentation links, citation URLs, badges |
| `FS` | File-system access | Instructions to read, write, move, or delete files beyond the Skill's own folder; broad globs | Reading the project's own files is normal for coding Skills |
| `CRED` | Credential or secret access | Reading, printing, or sending tokens, keys, `.env` files, keychains, SSH keys | Advice to *never* commit secrets; mentioning "API key" in setup notes |
| `INST` | Dependency installation or system modification | `pip`/`npm`/`brew`/`apt` installs; editing shell profiles; changing system configuration | Normal one-time setup steps |
| `SCRIPT` | Bundled-script execution | Running scripts shipped in the Skill's folder | A script that is present but never invoked |
| `PRIV` | Destructive or privileged operations | `sudo`, `chmod 777`, `rm -rf`, force-push, disk or database drops | Warnings that say "do not run X" |

Each rule has a stable ID of the form `<CATEGORY>-<NNN>`. Rule IDs are never reused once published, so the Sprint 2 prototype's IDs (for example `FS-001`) were retired when the final detectors (IDs from 101 for the newer categories) replaced them.

**Implemented in v1.0 (18 rules, `src/skillguard/detectors/`):**

| Category | Rules | What they match |
|---|---|---|
| CMD | CMD-001 to CMD-004 | A line in a shell code block; running a script file; a prompt-style `$ cmd` line; "run/execute `cmd`" in prose |
| NET | NET-001, NET-002 | An HTTP client (`curl`, `wget`, `Invoke-WebRequest`); a URL, counted only with a fetch action or inside shell code |
| FS | FS-101 to FS-104 | Reading files with a command; file-changing commands (`cp`, `mv`, `rm`, `sed -i`); write/delete APIs in Python or JavaScript; home or system paths |
| CRED | CRED-101 to CRED-103 | Credential files (`.env`, `.aws/credentials`, SSH keys); credential environment variables; "use/read/send" a password, API key, token, or credential |
| INST | INST-101 to INST-103 | Package installs; registry runners (`npx`, `uvx`); download-and-run pipes (`curl … \| sh`, the only **high**-level rule) |
| SCRIPT | SCRIPT-101, SCRIPT-102 | Running a script path; merely mentioning a script path (info only) |

`PRIV` is held out on purpose: adding it is the timed SWE 330 extensibility experiment (GQM Q1). **Bundled executables** are tagged when a Skill tells the agent to run them (`SCRIPT-101`, `CMD-002`), and the release's `has_scripts` flag records which folders ship scripts at all.

## 3. Finding record

Every finding contains `source`, `line`, `category`, `rule_id`, `evidence` (at most 160 characters, secrets masked), `explanation`, `context` (`prose`, `front_matter`, or `code:<language>`), and `review_level` (`info` / `review` / `high`). The `Finding` record rejects a missing field or an invalid level when it is created, and the pipeline rejects a finding whose line or context does not match the parsed Skill. Only `review` and `high` findings count toward the research outcomes; `info` findings are kept for transparency.

Categories are always reported separately. Any aggregate score is secondary and never replaces the per-category flags.

## 4. Context handling (known hard cases)

| Case | Handling in v1.0 | Error-taxonomy label |
|---|---|---|
| URL that is only a documentation link | `NET-002` stays at `info` unless a fetch action precedes it or it is inside shell code | `doc-url` |
| Front matter (metadata) | Never treated as an instruction; rules skip it | `metadata` |
| Code that is an example, not a step | Matches in non-shell code blocks are `info`, except file/credential API rules for Python/JavaScript | `code-example` |
| Comments in shell code | `#`, `//`, and `REM` lines are `info` | `code-fence` |
| Negated instruction ("never run `rm -rf`") | A cue (do not, never, avoid, must not, should not, cannot) within 40 characters before the match lowers it to `info` | `negation` |
| Mention without an instruction | Several prose rules need an action verb (run, use, read, send, install, …) before the match; otherwise `info` | `mention-only` |
| Benign setup command | Counted as `INST` at `review`: installing is a real capability even when routine | `benign-setup` |
| Quoted example output | Not handled; measured in validation | `quoted-example` |
| Context lost while parsing | Unclosed front matter or code fences are reported as parsing warnings | `parse-context` |

## 5. What SkillGuard does not establish

A finding does not show maliciousness, execution, harm, exploitability, or author intent. Absence of findings does not show that a Skill is safe.
