---
name: specifications-mode
description: Specification and prototype-support workflow for narrow product/domain specification work and spec-läge. Use when the user asks to arbeta med specifikationer, enter/leave spec-läge/spec mode, create or update business rules, verksamhetsbeskrivningar, requirements, implementation plans, priority groups, repo status, startup/introduktionsnivå, specstatus, sticky spec folders with domain subfolders, MCP-backed status tracking, or living product/domain specification documents; ask for confirmation only before actual repo-status changes; do not treat generic skill authoring or skill maintenance as specification work unless it describes the product/problem domain itself.
---

# Specifications Mode

## Scope

Specification work is intentionally narrow: it describes the problem domains, business/domain rules, product behavior, requirements, implementation plans, and decision-support prototypes for the idea/repo/product. Mechanical workflow documentation, such as creating or maintaining Codex skills, is not specification work by itself. Do not enter spec-läge only because the user asks to describe, write, or adjust a skill unless that work also creates or changes product/domain specifications.

## Core rule

When this skill is active and the repo is in **spec-läge**, create or edit only specification documents and clearly bounded decision-support prototypes under the sticky spec folder. Documentation files include `.md`, `.txt`, `.tex`, and other explicitly documentation-only formats. Prototype files are allowed only under `specs/prototyping/<poc-name>/` (or the repo's chosen spec folder equivalent) and only when they help resolve outstanding questions or provide decision evidence for specification work. Do not edit production source code, build files, generated program output, binaries, dependency files, or runtime application code while spec-läge is active.

## Repo status and mode changes

Always ask one explicit confirmation question before changing repo status when language suggests entering spec-läge, leaving spec-läge, or moving to implementation. Do not change durable specstatus until the user confirms. Suggested question: "Menar du att vi ska byta repo-status från `<current>` till `<target>`?"

Do not ask the status-change confirmation question when the user's wording only points to the repo status that is already current. Treat that as a continuation inside the current mode, not as a proposed mode change. For example, if durable specstatus or the active conversation already says `SPEC` and the user asks to "fortsätta i spec-läge", "jobba med specifikationerna", or similar, continue the specification workflow directly instead of asking whether to switch into `SPEC` again. Likewise, if the repo is already in `IMPLEMENTATION` and the user asks to continue implementation, do not ask whether to switch to `IMPLEMENTATION` again.

Track these repo statuses:

- `NON_SPEC`: default work outside spec-läge, including skill authoring/maintenance and general documentation that does not describe product/domain specs.
- `SPEC_PROPOSED`: language suggests spec-läge, but the user has not confirmed the status change yet.
- `SPEC`: confirmed spec-läge; specification documents and bounded decision-support prototypes under `specs/prototyping/<poc-name>/` may be created or edited.
- `IMPLEMENTATION_PROPOSED`: language suggests leaving spec-läge for implementation, but the user has not confirmed yet.
- `IMPLEMENTATION`: confirmed implementation work; code/build changes may be allowed, while living specs should still be updated when implementation status changes.

Mode rules:

- Enter `SPEC` only after the user confirms product/domain specification work, requirements, verksamhetsbeskrivningar, regler, or implementation planning.
- Leave `SPEC` only after the user confirms moving to implementation, coding, execution, or equivalent language.
- Track state in the conversation first and keep a durable specstatus file in the sticky spec folder when one exists, for example `specs/status/SPECSTATUS.md`.
- If the current mode is ambiguous, distinguish product/domain specification work from mechanical skill/tooling work. Use a proposed status and ask before switching.
- If durable specstatus exists, use it as a direct hint for ambiguous follow-up questions such as "vad ska vi arbeta med härnäst?". When current status is `SPEC`, propose continuing with specification work by reviewing open questions, unresolved decisions, contradictions, or the next living spec. When current status is not `SPEC`, briefly summarize the likely next non-spec work from status/plans and ask whether the user wants to switch into specification work only if the requested task would require that switch.
- Even after leaving spec-läge, keep living specification documents updated when implementation status changes.


## Short requests for questions

When the user asks a terse question such as "visa frågor", "frågor", "show questions", or equivalent, use current repo status and specstatus to resolve the ambiguity instead of asking what the word means.

- If the repo is in `SPEC` or the status indicates active specification work, treat "questions" as specification questions: show a concise list of unresolved questions, open decisions, contradictions, ambiguities, unclear descriptions, and reasoning gaps from `specs/status/` and the living specification documents. Prefer existing open-question sections over inventing new questions.
- If the repo has specstatus but is not currently doing specification work, still show a very short list of known open specification questions or likely unresolved specification areas, then ask whether the user wants to switch back to specification work before making documentation changes.
- If no specstatus or specs exist, say that no durable specification question list exists yet and offer to scan the repo to create a first draft of specification questions. Do not create spec files until the user confirms the intended specification work/status when a status change would be required.

## Specification files

Prefer Markdown (`.md`) for specifications unless the user requests another documentation format. Keep specifications in one sticky folder for the repo. If no spec folder exists, choose a short clear name such as `specs/`, create it, and keep using that same folder for future specification work. Use subfolders for distinct domain areas to avoid a messy flat spec tree.

Use at least these specification types and default subfolders:

1. **Verksamhetsbeskrivningar och regler** in `specs/domains/`: business/domain descriptions, rules, constraints, glossary, and reasoning.
2. **Implementationsplaner** in `specs/plans/`: prioritized implementation plans with action-level statuses. Keep plan history in the matching `document.Changelog.md` file.
3. **Beslut (Decisions)** in `specs/decisions/`: durable decision records that state the chosen option, date, context, alternatives, consequences, and links to supporting evidence or affected plans. Use these when a choice should remain traceable after the conversation ends.
4. **Underlag (Evidence)** in `specs/evidence/`: research notes, source summaries, observations, experiments, constraints, and other material that supports decisions or requirements without itself being the decision. Keep evidence factual and separate from conclusions.
5. **Arkitektur** in `specs/architecture/`: architecture descriptions, system boundaries, component relationships, interfaces, quality attributes, and architectural constraints. Link to decisions and evidence when architecture choices depend on them.
6. **Scheman (Schemas)** in `specs/schemas/`: data-bearing contracts that support specification work, for example JRDL schemas with pure JRDL types, XML schemas, JSON schemas, or other explicit contract formats. Keep schemas focused on contractual data shape, validation, and documentation metadata; put explanatory domain reasoning in `domains/`, decisions in `decisions/`, and architecture implications in `architecture/`.
7. **Specstatus** in `specs/status/`: current mode, introduction level, living documents, and implementation status signals. Keep status history in the matching `document.Changelog.md` file.
8. **Prototyping** in `specs/prototyping/`: disposable or exploratory proof-of-concept folders used only in spec-mode to answer open questions or support decisions. Each POC gets its own subfolder.
9. **Temporära exportdokument** in `specs/tmp/`: generated, non-authoritative documents requested for short-term review, for example a `.tex` summary of open questions. These files must clearly state that they are temporary, volatile, and not governing specification sources.

Additional types are allowed when useful, for example test strategy documents. Put each distinct domain area in its own subfolder when it grows beyond one focused document. Keep schemas, decisions, evidence, and architecture separate even when they refer to the same topic: schemas define data-bearing contracts, evidence supports, decisions choose, and architecture describes the resulting structure or constraints.

## JRDL schema syntax for specifications and POCs

JRDL (`.jrdl`) is our JSON-RPC Definition Language for data-model and operation contracts. A JRDL file can define reusable data types, JSON-RPC calls, imports, and transport metadata. Keep JRDL in `specs/schemas/` when it is part of our living specification, and treat it as hand-written source.

Native scalar types are `string`, `integer`, `boolean`, and `float`. Extended definitions are `enumeration`, `set`, `dictionary`, and `object`; these can be referenced by object members, call parameters, return values, dictionaries, and other objects.

Members, parameters, and returns may have an optional `min max` cardinality pair. Omitted cardinality means mandatory single value (`1 1`); `0 1` means optional single value; `0 -1` means optional unbounded array; and values such as `0 40` mean optional arrays with an upper bound. Arrays use the same type names as scalar values. A member array can be declared as a named array by adding `named` after the cardinality, for example `member "tags" "string" 0 -1 named`, which represents an object whose values all have the declared item type.

Use these core JRDL forms:

```jrdl
enumeration <name> <"integer"|"string">
	value <value> [documentation <text>]

set <name>
	value <value>

dictionary <name> <type|extended type>

object <name> [extends <object>] [documentation <text>]
	member <name> <type|extended type> [min max [named]] [validation <regexp>] [documentation <text>]

call <name> [documentation <text>]
	parameter <name> <type|extended type> [min max] [validation <regexp>] [documentation <text>]
	return <name> <type|extended type> [min max] [validation <regexp>] [documentation <text>]
```

Enumeration base types are `integer` or `string`. Enumeration values may carry ordinary `documentation <text>` metadata for both integer and string enumerations; do not reserve integer-enum documentation for generated C-style constant names unless a specific downstream generator contract explicitly requires that. A `set` is always integer-backed; each declared value is represented as one bit. A `dictionary` is represented as a JSON object with string keys and values of the declared type. An `object` can extend another object and can use `validation <regexp>` and `documentation <text>` on members. Call parameters and returns use the same cardinality, validation, and documentation style as members.

Operation files can declare metadata before calls:

```jrdl
jsonrpc "2.0"
protocol "line"
url "http://localhost:1080/my/service"
is-array "false"
```

`jsonrpc` declares the JSON-RPC version, `protocol` declares transport such as `line` or `http`, `url` declares the HTTP path or endpoint, and `is-array` controls whether generated client code sends JSON-RPC `params` as an array instead of an object.

JRDL supports imports with prefixes for local files, relative files, and URL-based schemas:

```jrdl
import "types.jrdl" with prefix "s0"
import "../other_types/types.jrdl" with prefix "s1"

call "GetPersonInfo"
	parameter "extra_info" "s1:ExtraInfo" 0 1
	return "person" "s0:Person"
```

Use prefixed references such as `s0:Person` when referring to imported types. Keep imported schemas explicit and local when possible so POCs remain reproducible.

## Specification prototyping

Prototyping is allowed as part of specification work only while the repo is in confirmed `SPEC` mode. A prototype must be a bounded proof of concept that helps resolve outstanding questions, compare alternatives, validate assumptions, or create decision evidence. A recommended POC must be small enough to implement within one working session. It must not become production implementation by stealth.

Place every POC in its own folder under the sticky spec folder's `prototyping/` directory, for example `specs/prototyping/coverage-formula-poc/`. Keep any notes, input data, scripts, and outputs for that POC inside its folder unless the user explicitly chooses another spec-folder structure. Summarize every created POC in the collection README, for example `specs/prototyping/README.md`, with status `OPEN` or `FINISHED`.

Recommend prototyping to the user when a small one-session experiment can provide fast guidance for continued spec work, especially for formulas, data-shape validation, UI flow sketches, generator/balance assumptions, migration/recovery rules, or ambiguity that would otherwise lead to speculative implementation planning.

Prefer Python for POCs because it is quick to write, inspect, and discard, but allow other languages or tools when they fit the question better. Keep dependencies minimal and documented in the POC folder.

When a POC uses our data-model contracts (`.jrdl`), treat the JRDL files as the authoritative contract input rather than as generated output. These contracts can be used with Alpha's `jrdl2python` to generate Python models for the POC, and they can also be used through `jrdl2openrpc` followed by `openrpc-generator` to generate bindings or clients in any needed target language. Do not commit generated code in POC folders. Instead, make code generation an explicit first step in the POC build and run workflow so generated models or language bindings are recreated locally before building, testing, or running the POC.

Every POC must include verifying test cases and regression tests that can be rerun to prove the observed behavior stays stable while the specification question is being evaluated. These tests can be lightweight, but they must document expected outcomes and fail visibly when the POC no longer supports its stated conclusion.

Every POC must also document how its experience feeds back into the rest of the specifications. At minimum, the POC README should state whether the POC is intended as decision evidence, hypothesis/plan verification, risk discovery, or rejected exploration, and it should link to the affected questions, decisions, schemas, domain rules, architecture notes, evidence notes, or implementation-plan actions. When a POC changes the recommended direction, update the relevant living specifications or create a decision/evidence document in the same change; if the POC is still only indicative, keep the affected question open and state what remains unresolved. The collection README should summarize this feedback status so future work can see whether each POC has already influenced decisions, plans, schemas, or only remains candidate evidence.

Do not read existing POC folders by default. Read a POC only when the current specification task explicitly needs that prototype, when its summary in the collection README indicates relevant evidence, or when the user asks for prototype history/details. Prefer the collection README summary first.

Do not create or extend spec-mode POCs when the repo is in `NON_SPEC`, `IMPLEMENTATION_PROPOSED`, or `IMPLEMENTATION`; ask for or confirm the appropriate status first when needed.

## Document changelogs

Keep changelog/history sections out of ordinary specification documents. For every Markdown document that needs history, create or update a sibling changelog file named `document.Changelog.md`, where `document.md` becomes `document.Changelog.md`. Examples: `item-engine.md` -> `item-engine.Changelog.md`, `SPECSTATUS.md` -> `SPECSTATUS.Changelog.md`, and `SKILL.md` -> `SKILL.Changelog.md`.

Do not read `*.Changelog.md` files by default. Read them only when specification work requires historical investigation, audit context, status reconstruction, or explicit user-requested history. Current-state work should rely on the non-changelog specification documents first.

When updating a document and its history matters, add one changelog row to the matching `*.Changelog.md` file using the exact format `- <YYYY-MM-DD>: <comment>`. Changelog files are reverse chronological: put new entries at the top, directly under the title or any fixed introductory text, so the newest change is easiest to find. Do not use date subheadings such as `## <YYYY-MM-DD>` inside changelog files, and do not add a `## Changelog`, `## Senaste lägesändringar`, or similar history section to the primary document. Keep only the mandatory final history-reference footer in the primary document.

## History reference footer

Every primary specification Markdown document must end with a final `## Historik` section whose final bullet points to the matching changelog file when it exists. Example bullet: `- Ändringshistorik finns i document.Changelog.md.` If the changelog file does not exist yet, the final bullet must instead say that changes will be saved in the corresponding file. Example bullet: `- Ändringar kommer att sparas i document.Changelog.md.`

Keep this footer as the last content in the primary document so readers can find history without loading it by default. Do not put actual changelog entries in the footer; entries belong only in the matching `*.Changelog.md` file.

## Startup/introduction level

At session start or before first spec change, classify the repo's startup/introduction level and record it in specstatus when a status file exists:

- `NONE`: no specs exist. Propose analyzing/scanning source code to build preliminary verksamhetsbeskrivningar before creating draft specs.
- `UNSTRUCTURED`: specs or documents exist but lack structure. Propose organizing them into sticky folders such as `specs/domains/`, `specs/plans/`, and `specs/status/` before adding much new content.
- `STRUCTURED`: sticky spec folder and clear subfolders exist. Continue updating existing living documents and statuses.

## MCP coordination

If MCP support is available in the current session, use it as a source of truth or synchronization aid for at least implementation priority, actions, and status. Prefer MCP resources/templates over ad-hoc inference when they expose project planning data. Reflect relevant MCP-backed status changes in implementation plans and specstatus without exposing sensitive data unnecessarily.

## Business descriptions and rules

For verksamhetsbeskrivningar, regularly review for:

- direct contradictions
- ambiguity or terms with multiple possible meanings
- unclear descriptions
- direct gaps in reasoning or missing prerequisites

A review is not required after every edit, but perform one periodically, whenever the user asks, or before using the document as the basis for implementation. Record review results in the relevant document or in a companion status section. Regularly compress documentation text to reduce future agent context cost, but preserve meaning, traceability, and enough detail for implementation.

## Refresh specifications

When the user asks to refresh, synchronize, reconcile, or realign specifications, treat the request as a full specification refresh of the sticky spec folder. The goal is to make the living specification set internally consistent, decision-aware, and ready for the next round of planning without silently turning unresolved specification questions into implementation assumptions.

Refresh workflow:

1. Identify the sticky spec folder, current specstatus, living domain documents, architecture notes, schemas, decision records, evidence notes, implementation plans, and existing open-question or outstanding-question documents. Prefer current primary documents first; read `*.Changelog.md` files only when history is needed to resolve ambiguity or reconstruct why a statement changed.
2. Synchronize related specification documents. When new information appears in only one place, propagate the meaning to other documents that discuss the same rule, term, decision, schema, architecture constraint, plan dependency, or open question. Preserve each document type's responsibility: domain/rule documents explain behavior and terms, schemas define data contracts, decisions record choices, evidence records support, architecture records structure and constraints, plans record execution order, and status documents record current state.
3. Detect contradictions, stale statements, duplicate wording with diverging meaning, missing links between decisions and affected documents, and terminology drift. Resolve straightforward inconsistencies directly when the governing decision or newer source is clear. When the correct resolution is not clear, keep both sides traceable and convert the conflict into an explicit outstanding specification question instead of guessing.
4. Use git history when chronology matters. If current documents conflict or a statement's intended ordering is ambiguous, inspect relevant commits with commands such as `git log -- <path>`, `git show <commit> -- <path>`, or `git blame <path>` to reconstruct the timeline. Use that timeline as decision evidence, not as automatic authority: a newer change may still be wrong if it contradicts a durable decision.
5. Re-evaluate implementation plans after specifications and decisions are coherent. Rethink the plan from the refreshed specification/decision state and what is best for the product now, not merely by preserving the previous task order. Update priorities, blockers, statuses, and superseded actions as needed; append the required changelog entry for plan changes.
6. Finally, update or create `specs/status/outstanding-questions.md` unless the repo has clearly chosen another outstanding-question location. Distill the most important remaining **specification** work, including unresolved decisions, contradictions, unclear terms, missing evidence, and questions that block or materially affect implementation planning. Keep it focused: do not use it as a general coding backlog.

During a refresh, do not create production implementation work. If the repo is not already in confirmed `SPEC` mode and the refresh would require editing specification documents, follow the normal repo status confirmation rules before making durable specification changes.

## Open questions before implementation planning

Before creating or maintaining an implementation plan, review the relevant specification status and living spec documents for unresolved questions, open decisions, contradictions, ambiguities, unclear descriptions, reasoning gaps, and other unresolved items that would make implementation planning speculative. If any such question marks exist, the skill recommendation is to resolve or decide them first instead of creating or updating the implementation plan.

The user may still explicitly request that the implementation plan be created or updated despite unresolved question marks. In that case, proceed only with the requested plan work, make the unresolved items visible as blockers or risks in the plan, and keep recommending that all question marks be straightened out before implementation starts.

## Temporary open-question `.tex` export

When the user requests a generated `.tex` document with open questions, create a temporary, non-governing export that summarizes everything under `specs/` that still needs to be resolved or decided according to current specstatus and the living specification documents. Place it under `specs/tmp/` using a clear name such as `open-questions-YYYY-MM-DD.tex` so its path signals that it is temporary and volatile.

The export must clearly state inside the document that it is generated, temporary, volatile, and not a governing source of truth. It must point readers back to the durable source documents under `specs/status/`, `specs/domains/`, `specs/decisions/`, `specs/evidence/`, `specs/architecture/`, `specs/schemas/`, and `specs/plans/` as applicable. Do not treat the temporary `.tex` export as a replacement for resolving the underlying questions in the durable specs.

## Implementation plans

Implementation plans must contain:

- priority groups, for example `P0`, `P1`, `P2`, or named groups
- prioritized actions within each group
- one status per action
- a matching `document.Changelog.md` file with dates and what changed

Recommended action statuses:

- `OPEN`: planned and not started
- `IN_PROGRESS`: currently being worked on
- `RESOLVED`: completed and reflected in implementation or documentation
- `BLOCKED`: cannot proceed until a blocker is removed
- `DEFERRED`: intentionally postponed
- `SUPERSEDED`: replaced by another action or decision

Use ISO dates (`YYYY-MM-DD`) in `*.Changelog.md` entries.

## Working workflow

1. Announce the mode when entering or leaving spec-läge.
2. Confirm that planned edits are limited to specification documents and/or bounded POCs under `specs/prototyping/<poc-name>/` while in spec-läge.
3. Create or update the relevant `.md`, `.txt`, or `.tex` files, and ensure primary specification Markdown documents end with the required history-reference footer.
4. For business/rule docs, add review notes when contradictions, ambiguities, unclear descriptions, or reasoning gaps are found.
5. Before creating or maintaining implementation plans, check for unresolved question marks and recommend resolving them first; recommend a one-session POC with verifying test cases and regression tests when it can quickly clarify a question or provide decision evidence, unless the user explicitly asks to update the plan anyway.
6. For implementation plans, update action statuses in the plan and append history entries to the matching `*.Changelog.md` file whenever priorities or statuses change.
7. Compress overly long documentation sections when they can be shortened without making the text unclear. Lagom is best: reduce repetition and obsolete detail, not necessary context.
8. If implementation work later resolves or blocks plan items, update the living specification documents as part of the same work.

## Templates

Use `references/spec-templates.md` for concise templates for business/rule specifications, implementation plans, and specification status files.

## Historik
- Ändringshistorik finns i `SKILL.Changelog.md`.
