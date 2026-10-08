# Team Working Agreement

**Issue:** #6 · **Courses:** both · **Status:** Draft. Each member confirms by commenting on issue #6.

## Roles (Sprint 1, may rotate at sprint boundaries)

| GitHub | Role | Main responsibilities |
|---|---|---|
| Ibrahimatatri | Product Owner, research lead | Backlog and acceptance criteria; research question; analysis |
| Baiselaired | Scrum Master, architecture lead | Planning, check-ins, reviews, and retrospectives; architecture and ADRs |
| ixmecrash | Data pipeline and detector lead | Loader, parser, detectors, performance |
| skyr-csc | Validation and communication lead | Annotation and validation; report and presentation integration |

A role is not a substitute for shared work. Every member contributes code or research **and** reviews others' work.

## Meetings
- **Sprint planning:** first day of each sprint. Choose issues, owners, and acceptance criteria. Notes go in `docs/meeting-notes/YYYY-MM-DD-planning.md`.
- **Check-ins:** twice a week (async in the team chat is fine). Each member posts what they did, what they will do next, and any blockers. Blockers are copied to the relevant issue.
- **Sprint review and retrospective:** last day of each sprint, recorded in `docs/retrospectives/sprint-N.md`.

## GitHub workflow
- One issue → one owner → one branch named `issue-<n>-<short-name>`.
- No direct pushes to `main`. All changes go through a pull request.
- A PR states its purpose, linked issue, changes, testing, generated outputs, limitations, and requested reviewer (see `.github/pull_request_template.md`).
- **Review rule:** a PR is merged only after approval by a member other than its author.
- Board status (`Workflow` field): Backlog → Ready → In Progress → In Review → Done (or Blocked, with the reason stated in the issue).
- Never commit dataset files, secrets, or bulk generated output.

## Definition of done
An issue is done when its acceptance criteria are met; evidence is in the repository; the work is merged through a reviewed PR; tests or generated outputs are included where relevant; documentation is updated; AI use is logged; and the board status matches reality.

## AI-use process
Anyone who uses an AI tool adds a row to `ai-use-log.md` recording the tool, purpose, prompt summary, what was accepted, modified, or rejected, how it was verified, and any errors found. AI output is reviewed like any other contribution.

## Communication and conflict
Respond to review requests within 48 hours. Disagreements about scope go to the Product Owner; process disagreements go to the Scrum Master. Unresolved issues are raised at the next check-in and recorded.
