# v1 — project operating system (read FIRST in every session)

You are the ribosome of this project: cheap, forgetful, replaceable. Meaning lives in
the documents, not in the session. This file is your O(k) context.

## What this is
A living compiler of ontologies (docs/design/SPEC.md §0). Numbering: **v0 = ../archgen**
(a donor of scars, NOT a donor of code, except what's listed in docs/log/PLAN.md), **v1 = here**.

## Constitution of the method
docs/design/MODEL.md — the universal model of development (layers, cycle, roles, coverage,
the UNIVERSAL roadmap). On conflict with it, SPEC refines the mechanisms.

## If you are the OPERATOR of an organism (feature/operation, not core development)
Read docs/OPERATOR.md + `onto explain <root> <entity>` — that's enough;
the rest here is for engine developers.

## Reading order (for a new session 1–3 is enough)
1. this file; 2. docs/log/PLAN.md — where we are (phase statuses); 3. docs/log/JOURNAL.md — the last
2–3 entries. Deeper as needed: docs/design/SPEC.md (architecture), docs/design/NOT.md (prohibitions),
docs/log/DECISIONS.md (why it's so), docs/design/SCARS.md (v0), docs/log/PREDICTIONS.md (what to check).

## Hierarchy of truth (on conflict, the upper one wins)
1. the user's word in the current session → 2. docs/log/DECISIONS.md (accepted decisions)
→ 3. SPEC/NOT → 4. PLAN → 5. JOURNAL/chats/artifacts (derived).
A contradiction between documents = a bug: fix the document, record it in JOURNAL.

## Session protocol (mandatory)
- START: read points 1–3; do NOT begin code if the phase is unclear.
- WORK: a new decision → a line in docs/log/DECISIONS.md (D-number, status, why);
  a cancelled one — supersede, don't delete. Inexpressible/dropped → docs/design/UNEXPRESSIBLE.md
  (create on the first occurrence). An idea outside the current phase → JOURNAL "parking,"
  do NOT implement (NOT §26).
- FINISH: an entry in docs/log/JOURNAL.md (what was done/decided/opened, 5–10 lines) +
  `git add v1 && git commit` — a wave without a commit does not exist (S7 v0).
- PHASE EXAM: walk through docs/log/PREDICTIONS.md — fulfilled/not, mark it.

## Hard prohibitions (full list — docs/design/NOT.md, 36 items)
The core knows no languages (I1); no regex-DSL; extra=allow is forbidden;
F1 — an interpreter WITHOUT code generation; commit only v1/ (don't touch archgen);
"from the theorem" only for Derived; no batches in the ribosome.

## Artifacts outside the repo
"Anatomy of v1" diagram: claude.ai/code/artifact/2515e15d-cb36-410d-ab78-e97f94d5ed54
(source — docs/anatomy.html, edit it and republish to the same URL).
Claude memory: ~/.claude/projects/-home-the maintainer-dnaContract/memory/.
