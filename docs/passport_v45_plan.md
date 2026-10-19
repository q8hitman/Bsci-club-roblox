# v45 BSC Passport — implementation record

Owner: continue under the supervisor's decisions (2026-10-19). Supervisor accepted v44 and selected Passport only.
Backup: backup_before_v45_20261019; branch dev/v45 from5165e29. Work stays in the specified existing checkout.

Design decisions: extend the existing Profile menu, Shop snapshot, Profiles persistence and Batch Hall setter.
No geometry or currency/research reward changes. XP is cosmetic, derived from an idempotent evidence ledger:
10 per unique stage,25 per collectible,40 for the first completed arcade/lab/show activity,75 per weekly task.
Level=1+floor(XP/100). Historical verified stage/collection evidence receives the same one-time XP after migration.
Weekly tasks reset Monday00:00UTC: visit5 different worlds, traverse3 different checkpoints, finish2 different activity
categories. Server-owned evidence sets prevent repeated actions/claims from duplicating rewards. New levels only
unlock cosmetic titles through the existing achievement/title system. Student batch is optional from the existing
whitelist; no personal information or free text. All source evidence and week boundaries are server decisions.
Ruling: keep reward definitions in one versioned module for this unpublished development build. ConfigService is
available for a later live balance rollout; no external config publishing or live-data access is authorized here.

Persistence: add passport={stamps,visits,weekly} with defaults. Merge sets, preserve unknown existing profile fields,
and keep failed-load saving disabled. Weekly progress uses server UTC and only retains the newest week's sets.
XP is recomputed from evidence, not accepted from clients or trusted as a saved numeric balance.

Steps:
1. Pure Luau tests: legacy/default migration, duplicate rewards, exact week boundary, duplicate/premature claims,
   save/load/union merge and two independent profiles. Observe failure before implementation.
2. Passport definitions/state and server integration: trusted successful teleports/checkpoints/activity completions;
   batch setter reuse; existing Shop snapshot/action surface only, no XP-grant remote.
3. Extend Profile UI with overview/weekly/batch pages while retaining achievements/collection/cosmetics/times.
4. Static checks and Studio solo/two clients/phone, actual UI actions, denied forged requests, no geometry regressions.
5. Whole-branch independent review, localv45 build, evidence screenshots/report/handoff, push dev/v45, supervisor review.

Limits: actual published DataStore and real phone remain untested without owner-approved publishing/device access.
No publishing, merging, architectural changes, real campus claims, horror content or new external services.

Verified completion: all five implementation steps completed. Solo, two actual Studio clients, iPhone XR landscape, source checks, unchanged Workspace comparison and independent review are recorded in passport_v45_report.md. Push and supervisor response are tracked in REPORT_FOR_CHATGPT.md.
