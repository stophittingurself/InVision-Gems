from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import BatchScoringResult, CandidateInput, ScoringResult
from backend.scorer import score_batch, score_candidate

app = FastAPI(
    title="inVision U Candidate Scorer",
    description=(
        "AI-assisted candidate screening for inVision U admissions. "
        "All scores are advisory — final decisions rest with the admissions committee."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/score", response_model=ScoringResult, summary="Score a single candidate")
def score_single(candidate: CandidateInput):
    try:
        return score_candidate(candidate)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post(
    "/score/batch",
    response_model=BatchScoringResult,
    summary="Score and rank a list of candidates",
)
def score_multiple(candidates: list[CandidateInput]):
    if not candidates:
        raise HTTPException(status_code=400, detail="Candidate list is empty")
    try:
        ranked = score_batch(candidates)
        return BatchScoringResult(shortlist=ranked, total_evaluated=len(ranked))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
