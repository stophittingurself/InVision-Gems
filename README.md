# inVision U Candidate Scorer

AI-assisted candidate screening for inVision U admissions (Decentrathon 5.0 hackathon).

The system scores candidates across 5 dimensions using an LLM and returns structured, explainable recommendations to assist — not replace — the admissions committee.

## Quick Start

**Requirements:** Python 3.11+, a free [Groq API key](https://console.groq.com)

```bash
# 1. Clone and install
git clone <repo-url>
cd invision
pip install -e .

# 2. Set your API key
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 3. Run the API
uvicorn backend.main:app --reload
# API is now at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## API Usage

### Score a single candidate

```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aisha Nurlanovna",
    "age": 17,
    "essay": "When I was 14, my school had no computer lab. I spent three months writing letters to local businesses asking for donated laptops...",
    "achievements": ["Founded school coding club (40 members)", "Regional science olympiad — 2nd place"],
    "motivation_letter": "I come from a family where no one has a university degree...",
    "extra_activities": ["Part-time work at a local NGO"]
  }'
```

### Score and rank multiple candidates

```bash
curl -X POST http://localhost:8000/score/batch \
  -H "Content-Type: application/json" \
  -d @data/synthetic_candidates.json
```

### Response structure

```json
{
  "candidate_name": "Aisha Nurlanovna",
  "scores": {
    "leadership_potential":      {"score": 8.5, "reasoning": "..."},
    "growth_trajectory":         {"score": 9.0, "reasoning": "..."},
    "motivation_alignment":      {"score": 8.0, "reasoning": "..."},
    "communication_authenticity":{"score": 9.0, "reasoning": "..."},
    "resilience":                {"score": 8.5, "reasoning": "..."}
  },
  "overall_score": 8.6,
  "recommendation": "STRONG",
  "summary": "...",
  "ai_content_flag": false,
  "ai_content_note": null
}
```

## Scoring Dimensions

| Dimension | What it measures |
|---|---|
| `leadership_potential` | Initiative and ability to rally others |
| `growth_trajectory` | Journey arc over time, not just peak achievements |
| `motivation_alignment` | Genuine fit with inVision U mission |
| `communication_authenticity` | Personal voice; flags possible AI-generated text |
| `resilience` | Overcoming adversity |

**Recommendations:** `STRONG` (>=7.5) · `CONSIDER` (>=5.5) · `PASS` (<5.5)

## Data

`data/synthetic_candidates.json` contains 5 synthetic profiles for testing.
No real candidate data is included or stored.

## Limitations

- Scores are advisory only; human review is mandatory before any admissions decision.
- The AI content flag is a heuristic — it can produce false positives and must not be used to auto-reject.
- The model may reflect biases present in its training data; committee members should apply critical judgment.
- Stage 1 has no persistent storage; submitted data is processed in-memory only.

## Architecture

See [`docs/architecture.md`](docs/architecture.md).

## Roadmap

- **Stage 2 (Mar 29 - Apr 2):** Admissions dashboard (Next.js) + Telegram bot for candidate intake
- **Stage 3 (Apr 4-5):** Polish, final presentation
