# SkillGuard Architecture (Phase 2)

**Course:** SWE 330 Phase 2 (issue #14) · **Status:** Proposed for team review · **Code:** branch `issue-15-modular-skillguard`

SkillGuard is a **modular monolith with ports-and-adapters boundaries**: one Python process whose pure core (parse → detect → explain) never performs I/O, surrounded by adapters that read the GitSkills release or a local file and write tables and figures. The four views below use one notation (Mermaid flowcharts and a sequence diagram; solid arrows = "depends on" or "calls", dashed = "reads/writes data"). Decisions behind them are in [`docs/decisions/`](../decisions/).

## View 1: System context

*Purpose: show the boundary.* SkillGuard has no network access and no execution path for Skill content; everything outside the box is data.

```mermaid
flowchart LR
    team["Student developer-researchers<br/>(run pipeline, read reports)"]
    raters["Two team raters<br/>(manual validation)"]
    release[("GitSkills release v1.0.0<br/>44 GB SQLite, Zenodo 21875637")]
    local[("One local SKILL.md")]
    subgraph boundary["SkillGuard (single Python process, no network, never executes Skill content)"]
        sg["Scanner + analysis pipeline"]
    end
    out[("results/ tables, figures/,<br/>validation sheets")]
    report["SWE 330 / SWE 380 reports"]
    team -->|make pipeline / scan-file| sg
    release -. "read-only (mode=ro, immutable)" .-> sg
    local -. read as text .-> sg
    sg -. writes .-> out
    out --> report
    raters -->|label sheet| out
```

## View 2: Modules and dependency direction

*Purpose: show the central design decision.* Dependencies point inward to `domain`. The core (`domain`, `parsing`, `detectors`, `scan`, `analysis`) imports no I/O modules; detectors see only parsed lines. `tests/unit/test_architecture.py` fails the build on any arrow not drawn here (0 violations on 2026-10-26).

```mermaid
flowchart TB
    cli["cli<br/>(composition root, commands)"]
    subgraph adapters["adapters (I/O edge)"]
        gitskills["gitskills<br/>read-only SQLite: index, funnel, sample"]
        files["files<br/>one local SKILL.md"]
        report["report<br/>CSV tables, figure"]
    end
    subgraph core["core (pure, standard library only)"]
        scan["scan<br/>parse once, run detectors, de-duplicate"]
        detectors["detectors<br/>registry + cmd, net, fs, cred, inst, script<br/>(_rules: shared Rule engine)"]
        parsing["parsing<br/>front matter / prose / code:lang"]
        analysis["analysis<br/>reuse groups, outcomes, effect sizes"]
        domain["domain<br/>Skill, Line, Finding, review levels"]
    end
    baseline["baseline<br/>(Sprint 1 single file, kept for comparison)"]
    cli --> gitskills & files & report & scan & analysis
    scan --> detectors --> parsing --> domain
    scan --> parsing
    detectors --> domain
    scan --> domain
    analysis --> domain
    gitskills --> domain
    files --> domain
```

The extension point is the detector registry (`detectors/__init__.py`): a new category is one module exposing `CATEGORY` and `detect(lines)`, plus one registry entry (ADR-0003). Analysis, outputs, and the figure pick up new categories from the registry without code changes.

## View 3: Pipeline data flow

*Purpose: show persistence and reproducibility.* Each step reads the previous step's file, so steps can be re-run independently, and every output is deterministic (two full runs produced byte-identical files).

```mermaid
flowchart LR
    db[("Release .db<br/>3,797,117 files")] -->|"index (63 s)<br/>one pass, GROUP BY hash"| idx[("data/interim/index.sqlite<br/>1,877,981 hashes")]
    idx -->|"sample (9 s)<br/>5,000 lowest hashes per reuse group"| smp[("sample.jsonl<br/>15,000 Skills")]
    db -. "content by hash" .-> smp
    smp -->|"scan (70 s)"| fnd[("findings.csv 207,645<br/>outcomes.csv 15,000")]
    fnd -->|"analyze (11 s)"| res[("results/sprint2/*.csv<br/>figures/*.png")]
    idx -->|population tables| res
    fnd -->|annotation-sample| val[("validation sheet + key<br/>120 Skills, 30 double-coded")]
```

## View 4: Scanning one Skill (sequence)

*Purpose: show where explanation and safety are enforced.* Text is parsed once; every finding carries category, rule ID, line, masked evidence, explanation, review level, and context.

```mermaid
sequenceDiagram
    participant C as cli scan
    participant G as adapters.gitskills
    participant S as scan.scan
    participant P as parsing.parse
    participant D as each detector
    participant R as _rules.evaluate
    participant A as analysis.outcomes
    C->>G: read_sample(sample.jsonl)
    G-->>C: Skill(sha, text, source) + metadata
    C->>S: scan(skill)
    S->>P: parse(text)
    P-->>S: Line(no, text, context)[]
    loop registry order
        S->>D: detect(lines)
        D->>R: evaluate(CATEGORY, RULES, lines)
        R-->>D: Finding[] (negation and doc URLs set to info, secrets masked)
        D-->>S: Finding[]
    end
    S-->>C: findings, de-duplicated by (rule, line), sorted
    C->>A: outcomes(text, findings, categories)
    A-->>C: has_<category>, any_risky, lengths (info findings never count)
```

## Quality attributes and where they live

| Quality (GQM) | Mechanism | Evidence (Phase 2) |
|---|---|---|
| Extensibility (Q1) | Detector registry; detectors are declarative `Rule` lists | Adding PRIV in a pilot: 0 core modules modified, 2 edit sites (vs 4 in the baseline) |
| Change isolation (Q2) | Inward dependencies, conformance test | 0 violations; adding PRIV changed no other category's findings on 3,000 Skills |
| Reproducibility (Q3) | Deterministic sample (hash order), sorted CSVs, fixed float precision, `make pipeline` | 10 of 10 artifacts byte-identical across two full runs |
| Performance (Q4) | Single pass index in SQLite; streaming scan | Same rules: 1.55× the baseline's runtime; all 23 rules: 228 Skills/s, 133 MB peak |
| Explainability and testability (Q5) | `Finding` record; one positive + one negative test per rule | 100% field completeness; 100% detector/parsing coverage |
