# Model Card: PawPal+ AI Pet Care Advisor

## Overview
PawPal+ AI extends my Module 2 project, PawPal+ (a pet care scheduler), with an AI advisor.
A user asks a pet care question, the system retrieves matching sections from 10 cited pet care
notes files, and Gemini suggests care tasks based only on those notes. Every suggestion is
validated by code and must be reviewed and approved by the user before it is scheduled.

| Item | Detail |
|---|---|
| Model | Google Gemini `gemini-3.6-flash`, backup `gemini-3.5-flash-lite` (temperature 0.2, JSON output) |
| AI feature | Retrieval-Augmented Generation (RAG) with keyword + species scoring |
| Knowledge base | 10 markdown files (9 animals + emergencies), every section cited to ASPCA, AKC, AAHA, VCA, RSPCA, PDSA, RVC, Cornell, Merck/MSD Vet Manual, or CDC |
| Human-in-the-loop | User can edit, untick, approve, or discard every AI suggestion |
| Intended use | Helping pet owners build a routine care schedule |
| Not intended for | Medical advice, emergencies, medication or dosing questions |

## Limitations and Biases
- **Small, fixed knowledge base.** Only 9 kinds of animals are covered. Questions about other
  animals (ferrets, horses, chickens) get no tasks.
- **Keyword retrieval is simple.** It matches words, not meaning. Words not in my lists
  (like "pup" or "doggo") may not find the right notes.
- **Source bias.** Most sources are from US, UK, and Australian organizations, so advice
  like rabbit vaccines may not apply everywhere. The notes are in English only.
- **Emergency detection uses keywords.** It can give false alarms ("Can my dog eat grapes?"
  triggers it) and can miss emergencies that use other words ("my dog swallowed something weird").
- **Gemini is not fully consistent.** The same question can give different tasks on different runs.
- **Conflict checks use exact times only.** A 30-minute task at 07:00 and a task at 07:15 are not flagged.

## Misuse and Prevention
| Possible misuse | How the system reduces it |
|---|---|
| Treating the app as a vet in an emergency | Emergency words are checked **before** the AI runs; the user gets a red "contact your vet" message with the ASPCA Poison Control number, and no tasks are scheduled |
| Asking for medical or dosing advice | The prompt tells Gemini to answer only from the notes, and the notes contain no dosing information. Every notes file says it is not a substitute for a veterinarian |
| Off-topic use ("write my essay") | If no notes match, the system answers "I don't have pet care notes about that" without calling Gemini |
| AI adding wrong or made-up tasks | Code validates every field, invalid suggestions are rejected and shown, and nothing is added until the user approves |
| Leaking the API key | The key lives in `.env`, which is in `.gitignore` and never committed |

A remaining risk: a user could still approve a bad suggestion without reading it. The app
shows the source for every task to make checking easier, but the final decision is the user's.

## Testing Results
| Test type | Result |
|---|---|
| pytest (`tests/`), Gemini replaced with a fake | 23/23 passed (10 original scheduler tests + 13 AI tests) |
| `evaluate.py`, real Gemini, 9 cases | 9/9 cases, 37/37 checks passed |
| Hallucination check (ferret vaccines, not in notes) | Passed: 0 tasks invented |
| Real 503 "server busy" error | Handled: retried, then a friendly message, no crash (see `assets/sample_log_503_retry.txt`) |

## What Surprised Me While Testing
- **The same question did not always give the same result.** "What should my puppy eat?"
  returned 4 valid tasks one time and 0 tasks another time, even with temperature 0.2.
  Nothing crashed and nothing was rejected, so I only noticed because of the log file. I think
  the cause was the missing puppy age, since the notes give different meal counts for each age.
  I fixed it by logging Gemini's answer when it returns no tasks and telling it to assume the
  most common case and say what it assumed.
- **The Gemini server was busy (503) much more often than I expected.** My first version just
  crashed. I added a retry with a backup model, error handling, and logging.
- **Retrieval alone was not safe for emergencies.** "My dog ate chocolate" retrieved the
  Dog feeding notes instead of the emergencies file, because the "dog" bonus outweighed
  everything else. I added a separate emergency check that runs before retrieval.
- **pytest tried to run my saved output file.** I saved results as `test_results.txt`, and
  pytest treats any `test*.txt` file as a test. PowerShell also saved it as UTF-16, which
  pytest could not read. I renamed it and saved it as UTF-8.

## AI Collaboration
I used Claude as an assistant to plan the project, explain my old code, research and cite the pet care notes, and draft code. I reviewed, tested, and changed its suggestions before committing them.

**A suggestion I accepted:** Testing with a fake Gemini. Claude suggested replacing
`ask_gemini` with a fake function in pytest (mocking). I accepted it because real API calls
would make tests slow, use my quota, give different answers each time, and fail whenever
the server is busy. Now my 13 AI tests run in about a second and always give the same result.

**Suggestions I rejected or changed:**
- **Scoring inside `retrieve()`.** Claude wrote the scoring logic inside `retrieve()`. I split
  it into a separate `score_chunk()` function so each part does one job and is easier to test.
- **Model name in `.env`.** Claude put the model name in the `.env` file. I changed it to be
  written in the code, the way my lab did it, because it is simpler and Gemini is called from
  only one place.
- **The architecture diagram.** Claude's first diagram was too busy to read. I asked for a
  simpler version that shows the main path in one line.
- **Approve-then-remove.** The first version only let users untick suggestions. I wanted users
  to fix a suggestion's time or priority **before** approving, so I chose to add an editable
  table instead.