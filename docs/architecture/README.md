# SkillGuard Architecture (final, Phase 3)

**Course:** SWE 330 Phase 3 (issue #26) · **Status:** Final design as of 2026-11-16 · What changed since Phase 2 and why: [`changes-since-phase2.md`](changes-since-phase2.md) · Phase 2 views: [`phase2-views.md`](phase2-views.md)

SkillGuard is a **modular monolith with ports-and-adapters boundaries**: one Python process whose core (parse → detect → validate findings) never reads files or the database, surrounded by adapters for local files, the GitSkills release, and reports. Detection is a set of **plugins**, one per capability category, behind one `Detector` interface. The four views below use one notation (Mermaid; solid arrows = "depends on" or "calls", dashed = "reads/writes data"). Decisions behind them are in [`docs/decisions/`](../decisions/). A code reading guide is in [`zaid-reading-guide.md`](zaid-reading-guide.md).

## View 1: System context

*Purpose: show the boundary.* SkillGuard has no network access and no way to execute Skill content; everything outside the box is data.

```mermaid
flowchart LR
    team["Student developer-researchers<br/>(run pipeline, read reports)"]
    raters["Two team raters<br/>(manual validation)"]
    release[("GitSkills release v1.0.0<br/>44 GB SQLite, Zenodo 21875637")]
    local[("Local SKILL.md files<br/>or a folder of repositories")]
    subgraph boundary["SkillGuard (single Python process, no network, never executes Skill content)"]
        sg["Scanner + study pipeline"]
    end
    out[("results/ tables, figures/,<br/>validation sheets")]
    report["SWE 330 / SWE 380 reports"]
    team -->|make pipeline / make census / scan-file| sg
    release -. "read-only (mode=ro, immutable)" .-> sg
    local -. read as text, size-capped .-> sg
    sg -. writes .-> out
    out --> report
    raters -->|label sheet| out
```

## View 2: Modules and dependency direction

*Purpose: show the central design decision.* Dependencies point inward to `domain`. The core (`domain`, `parsing`, `detectors`, `pipeline`, `analysis`) imports no I/O modules, and detectors see only parsed records. Two tests fail the build on any arrow not drawn here: `tests/unit/test_architecture.py` and `tests/unit/test_layer_boundaries.py` (0 violations).

```mermaid
flowchart TB
    cli["cli<br/>(commands)"]
    research["research<br/>(GitSkills study: index, sample, census, analysis, validation sheet)"]
    subgraph adapters["adapters (I/O edge)"]
        files["files<br/>local SKILL.md / folders"]
        gitskills["gitskills<br/>read-only SQLite release"]
        report["report<br/>folder-scan CSVs"]
        tables["tables<br/>result tables, figure"]
    end
    subgraph core["core (pure, standard library only)"]
        pipeline["pipeline<br/>parse once, run plugins, validate findings, group copies"]
        detectors["detectors<br/>Detector interface + 6 plugins<br/>(_rules: shared context, masking)"]
        parsing["parsing<br/>front matter / prose / code:lang"]
        analysis["analysis<br/>reuse groups, outcomes, effect sizes"]
        domain["domain<br/>Skill, ParsedSkill, ParsedLine, Finding"]
    end
    baseline["baseline<br/>(Sprint 1 single file, kept for comparison)"]
    cli --> research & pipeline & files & report
    research --> gitskills & tables & pipeline & analysis
    report --> pipeline
    pipeline --> parsing & detectors & domain
    detectors --> domain
    parsing --> domain
    analysis --> domain
    gitskills --> domain
    files --> domain
```

**Extension point.** A new capability category is one module with a `Detector` subclass (`category` and `detect(parsed)`) plus one entry in `detectors/__init__.py: default_detectors()`. Pipeline, outcomes, tables, and the figure pick up new categories from the registry without edits (ADR-0010).

## View 3: Pipeline data flow

*Purpose: show persistence and reproducibility.* Each step reads the previous step's file, so steps can be re-run separately, and every output is deterministic.

```mermaid
flowchart LR
    db[("Release .db<br/>3,797,117 files")] -->|"index (~1 min)<br/>one pass, GROUP BY hash"| idx[("data/interim/index.sqlite<br/>1,877,981 hashes")]
    idx -->|"sample (~10 s)<br/>5,000 lowest hashes per reuse group"| smp[("sample.jsonl<br/>15,000 Skills")]
    db -. "text by hash" .-> smp
    smp -->|"scan-sample"| fnd[("findings.csv + outcomes.csv")]
    fnd -->|analyze| ress[("results/sample/")]
    fnd -->|annotation-sample| val[("validation sheet + key<br/>120 Skills, 30 double-coded")]
    db -. "one sequential pass" .-> cen["census<br/>8 worker processes"]
    idx --> cen
    cen --> cout[("census_outcomes.csv<br/>1,612,927 rows, no text")]
    cout -->|analyze| resc[("results/census/<br/>final results")]
```

## View 4: Scanning one Skill (sequence)

*Purpose: show where explanation and safety are enforced.* Text is parsed once, every plugin sees the same parsed lines, and the pipeline checks every finding before accepting it.

```mermaid
sequenceDiagram
    participant C as cli / research
    participant P as pipeline.scan_skill
    participant R as parsing.parse_skill
    participant D as each Detector plugin
    participant E as detectors._rules
    C->>P: scan_skill(Skill)
    P->>R: parse_skill(skill)
    R-->>P: ParsedSkill (lines with context, warnings)
    loop default_detectors()
        P->>D: detect(parsed)
        D->>E: evaluate_rules / review_level / make_finding
        E-->>D: Finding (evidence masked, level from context)
        D-->>P: Finding[]
        P->>P: reject a finding with the wrong source, category, line, or context
    end
    P-->>C: findings, de-duplicated and sorted (info findings never count toward outcomes)
```

## Quality attributes and the evidence for them

| Quality (GQM) | Mechanism | Final evidence |
|---|---|---|
| Extensibility (Q1) | Plugin interface + registry; shared rule engine | Four real detector additions (#38): after the first, each touched 2 files and 0 core modules |
| Change isolation (Q2) | Inward dependencies, two conformance tests, finding validation in the pipeline | 0 dependency violations; 100% of existing tests passed after each addition |
| Reproducibility (Q3) | Deterministic sample, sorted outputs, fixed precision, `make pipeline` / `make census` | Byte-identical outputs across runs; setup in a fresh Python 3.15 environment |
| Performance (Q4) | One-pass index; parallel census | `results/evaluation/benchmark.csv`; census run time in the final report |
| Explainability and testability (Q5) | `Finding` validated when created and again in the pipeline; tests per rule | 100% field completeness; coverage in the final report |
