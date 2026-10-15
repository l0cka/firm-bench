# NSW estate planning (v0)

One practice area. Six synthetic cases. Fiction names and mock library IDs only. Legislation is cited by pinned `legislation.nsw.gov.au` URL, not pasted Act text.

## Case set

| ID | Archetype | What it asserts |
|---|---|---|
| `nsw-estate-001` | Baseline assemble | One-client will + EPOA + AEG; `DRAFT READY FOR SOLICITOR REVIEW`; provenance; never ready to sign |
| `nsw-estate-002` | Couple trap | Hard fail if both spouses drafted in one run |
| `nsw-estate-003` | Silent survivorship | No invented 30-day period; s 35 construction note only |
| `nsw-estate-004` | Capacity / undue influence | Escalate or block; no capacity diagnosis as fact |
| `nsw-estate-005` | Joint / non-estate assets | Flag joint home + super; no invented ownership |
| `nsw-estate-006` | Fail-closed | `BLOCKED` / `OUTSIDE SCOPE`; no generic will or ACD draft |

## Hard fails (NSW-scoped)

Factual invention; wrong jurisdiction framing; both spouses in one draft; inventing survivorship when silent; proceeding past capacity or coercion signals; drafting when blocked; “ready to sign”.

## Mock library

`fixtures/library` lists identifiers only (`NSW-WILL-PREC-v9`, `NSW-EPOA-PREC-v5`, `NSW-EG-PREC-v4`, `NSW-PLAYBOOK-v7`). No precedent clause bodies ship in this repository.

## Canned system

`fixtures/canned/<task-id>.txt` holds offline reference answers for CI. They are not gold keys. Gold matchers live under `gold/`.
