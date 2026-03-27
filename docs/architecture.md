# System Architecture — inVision U Candidate Scorer

## Overview

An AI-assisted candidate evaluation system for inVision U admissions.
The system **supports** the admissions committee; it never makes final decisions autonomously.

## Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│  Stage 2+                                                    │
│  ┌─────────────────┐        ┌──────────────────────────┐    │
│  │  Telegram Bot   │        │  Admissions Dashboard    │    │
│  │  (candidate     │        │  (Next.js, Stage 2)      │    │
│  │   intake)       │        │  shortlist + score cards │    │
│  └────────┬────────┘        └────────────┬─────────────┘    │
│           │                              │                   │
└───────────┼──────────────────────────────┼───────────────────┘
            │         HTTP/JSON            │
            ▼                              ▼
┌───────────────────────────────────────────────────────┐
│              FastAPI  (backend/main.py)               │
│                                                       │
│   POST /score          →  score single candidate      │
│   POST /score/batch    →  score & rank N candidates   │
│   GET  /health                                        │
└───────────────────────────┬───────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────┐
│              Scoring Engine  (backend/scorer.py)      │
│                                                       │
│  1. Build structured prompt from CandidateInput       │
│  2. Call Groq API (llama-3.3-70b-versatile)           │
│  3. Parse JSON response → ScoringResult               │
└───────────────────────────┬───────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Groq API    │
                    │ (free tier)   │
                    └───────────────┘
```

## Scoring Dimensions

Each candidate is scored 0–10 on five axes:

| Dimension | What it measures |
|---|---|
| `leadership_potential` | Initiative, rallying others, creating change |
| `growth_trajectory` | Journey arc and improvement over time, not peak achievements |
| `motivation_alignment` | Genuine fit with inVision U mission |
| `communication_authenticity` | Personal voice; flags AI-generated text |
| `resilience` | Evidence of overcoming adversity |

**Overall score** = arithmetic mean of the five axes.

**Recommendation thresholds:**
- `STRONG` >= 7.5
- `CONSIDER` >= 5.5
- `PASS` < 5.5

## Explainability

Every `ScoringResult` includes:
- Per-dimension score + 1-2 sentence reasoning
- `ai_content_flag` + `ai_content_note` (reviewed by humans, never used to auto-reject)
- `summary` — overall 2-3 sentence narrative

The admissions committee sees all reasoning, not just a final number.

## Data Flow

```
CandidateInput (JSON)
  → scorer.py builds prompt
  → Groq API returns JSON
  → parsed into ScoringResult
  → returned via FastAPI
  → committee reviews in dashboard (Stage 2)
  → committee makes final decision
```

## Ethical Constraints Enforced

- System prompt explicitly prohibits demographic/socioeconomic proxies
- `ai_content_flag` is advisory only — flagged candidates are reviewed, not rejected
- No personal data stored beyond the request lifecycle (Stage 1)
- Human-in-the-loop: final accept/reject is a dashboard action, not an API call

## Stage Roadmap

| Stage | Dates | Deliverable |
|---|---|---|
| 1 | Mar 27-29 | Scoring engine API + architecture + repo |
| 2 | Mar 29-Apr 2 | Dashboard + Telegram bot + demo video + README |
| 3 | Apr 4-5 | Polish + final presentation |
