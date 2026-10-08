> **Note (2026-10-07):** moved from `/Questions`. The original 12 questions are kept below unchanged. A revised list of 13 questions, aligned with the locked research question, follows them. Answers belong in `docs/elicitation/dataset-answers.md` and must cite their sources and separate confirmed dataset facts from project decisions.

# Dataset: GitSkills
# Proposal: We have elected to research the reuse of skills, specifically the amount of trust -- in terms of potentially dangerous executable data -- written into a skill over the number of copies and reuses of it. Subsequently, we intend to evaluate whether these skills that gain measurable trust are directed at particular AI models, to show whether particular models (or perhaps brands of models) are targeted and afforded more power than others.

This exercise is to create well-defined boundaries of what research is possible given the selected dataset, and to direct said research. List the source from which the response to each question is derived.

1. Describe the purpose and scope of the dataset.

2. Describe the schema of the dataset.

3. Which fields identify the Skill file, repository, file path, content, and collection date?

4. Can file_sha reliably identify Skills with identical content across different repositories? The dataset presentation mentions a content hash for each skill file, can that be used reliably to exclude duplicates, if any exist?

5. How should we define a “widely reused” Skill: two or more copies, a fixed number of copies, or a percentile?

6. How will the project identify potentially risky capabilities such as command execution, network access, file operations, and credential access?

7. How will the project distinguish actual instructions from examples, quoted code, warnings, and negated instructions?

8. Suggest general approaches to implementation -- that is, how to efficiently analyze the dataset in a way conducive to the proposal.

9. Propose tools that might help actualize the proposal's implementation -- that is, that would allow for approaches presented in the previous point.

10. How many Skills should we manually review to measure false positives, false negatives, and agreement between reviewers?

11. Evaluate whether there are any potential privacy concerns that could arise from use of the dataset.

12. Consider and present any ethical or security concerns related to the proposal.

---

## Revised dataset investigation questions (2026-10-07)

For each answer, identify the source used and distinguish confirmed dataset facts from proposed project decisions.

1. What is the purpose and scope of the GitSkills dataset?
2. What does each dataset record represent, and what is the dataset schema?
3. Which fields identify the Skill file, repository, file path, content, collection date, and related metadata?
4. Can `file_sha` reliably group identical Skill content across repositories, and what conclusions cannot be drawn from matching hashes?
5. How should the project define a "widely reused" Skill: a fixed threshold, reuse categories, a percentile, or a continuous measurement?
6. *(Superseded secondary question: AI-model targeting. Kept as possible future work.)* Does the dataset contain enough reliable information to determine whether a Skill explicitly targets or mentions a particular AI model?
7. How should SkillGuard identify capability signals such as command execution, network access, file operations, credential access, dependency installation, and bundled-script execution?
8. How can SkillGuard distinguish operative instructions from examples, quoted code, documentation, warnings, code fences, and negated instructions?
9. What implementation approach would efficiently load, filter, normalize, analyze, and summarize the dataset?
10. Which tools and libraries best support data loading, Markdown parsing, static detection, testing, statistical analysis, and reproducible reporting?
11. How many Skills should be manually reviewed to estimate false positives, false negatives, precision, recall, and agreement between reviewers?
12. What privacy, licensing, ethical, and security concerns must be considered when using public repository data and reporting the findings?
13. What do the dataset and available sources not establish, including actual execution, malicious intent, copying direction, trust, quality, safety, and real-world harm?
