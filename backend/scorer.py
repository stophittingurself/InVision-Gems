from __future__ import annotations

import json
import os

from groq import Groq
from dotenv import load_dotenv

from backend.models import (
    CandidateInput,
    DimensionScore,
    Recommendation,
    ScoringResult,
)

load_dotenv()

_client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """\
You are an expert admissions evaluator for inVision U — a fully-funded university \
focused on developing future leaders and entrepreneurs in Kazakhstan.

Your role is to assess candidates fairly based solely on their potential, growth \
trajectory, and authentic motivation — NOT on demographics, socioeconomic background, \
or polished self-presentation skills. A rough but genuine voice is valued over a \
perfect but hollow one.

You MUST return a single valid JSON object and nothing else.
"""

SCORING_TEMPLATE = """\
Evaluate the following candidate and return a JSON object with this exact structure:

{{
  "leadership_potential": {{"score": <0-10>, "reasoning": "<1-2 sentences>"}},
  "growth_trajectory": {{"score": <0-10>, "reasoning": "<1-2 sentences>"}},
  "motivation_alignment": {{"score": <0-10>, "reasoning": "<1-2 sentences>"}},
  "communication_authenticity": {{"score": <0-10>, "reasoning": "<1-2 sentences>"}},
  "resilience": {{"score": <0-10>, "reasoning": "<1-2 sentences>"}},
  "ai_content_flag": <true|false>,
  "ai_content_note": "<brief note if flagged, else null>",
  "summary": "<2-3 sentence overall assessment>"
}}

Scoring guidance:
- leadership_potential: evidence of initiative, rallying others, creating change
- growth_trajectory: focus on the JOURNEY and improvement arc, not peak achievements
- motivation_alignment: genuine alignment with inVision U mission (leadership, entrepreneurship, social impact)
- communication_authenticity: does the voice feel real and personal? flag if it reads like AI-generated text (overly formal transitions, generic phrases, no specific personal details)
- resilience: evidence of overcoming setbacks or adversity

---
Candidate: {name}, age {age}

Essay:
{essay}

Achievements:
{achievements}

Motivation Letter:
{motivation_letter}

Extra Activities:
{extra_activities}
"""


def _build_prompt(candidate: CandidateInput) -> str:
    return SCORING_TEMPLATE.format(
        name=candidate.name,
        age=candidate.age,
        essay=candidate.essay,
        achievements="\n".join(f"- {a}" for a in candidate.achievements) or "None listed",
        motivation_letter=candidate.motivation_letter,
        extra_activities="\n".join(f"- {a}" for a in candidate.extra_activities) or "None listed",
    )


def _parse_response(name: str, raw: str) -> ScoringResult:
    data = json.loads(raw)

    dimension_keys = [
        "leadership_potential",
        "growth_trajectory",
        "motivation_alignment",
        "communication_authenticity",
        "resilience",
    ]

    scores: dict[str, DimensionScore] = {
        k: DimensionScore(score=data[k]["score"], reasoning=data[k]["reasoning"])
        for k in dimension_keys
    }

    overall = round(sum(s.score for s in scores.values()) / len(scores), 2)

    if overall >= 7.5:
        recommendation = Recommendation.STRONG
    elif overall >= 5.5:
        recommendation = Recommendation.CONSIDER
    else:
        recommendation = Recommendation.PASS

    return ScoringResult(
        candidate_name=name,
        scores=scores,
        overall_score=overall,
        recommendation=recommendation,
        summary=data["summary"],
        ai_content_flag=bool(data["ai_content_flag"]),
        ai_content_note=data.get("ai_content_note"),
    )


def score_candidate(candidate: CandidateInput) -> ScoringResult:
    """Score a single candidate via Groq API."""
    prompt = _build_prompt(candidate)
    response = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    return _parse_response(candidate.name, raw)


def score_batch(candidates: list[CandidateInput]) -> list[ScoringResult]:
    """Score a list of candidates and return a ranked shortlist."""
    results = [score_candidate(c) for c in candidates]
    return sorted(results, key=lambda r: r.overall_score, reverse=True)
