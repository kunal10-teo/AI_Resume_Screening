# ============================================================
# ADVANCED CANDIDATE RANKING
# ============================================================

def calculate_final_ranking_score(
    skill_score,
    semantic_score,
    experience,
    project_score=0
):
    """
    Advanced candidate ranking score.

    Skill Match       = 40%
    Semantic Match    = 30%
    Experience       = 15%
    Projects          = 15%
    """

    # --------------------------------------------------------
    # Experience Score
    # --------------------------------------------------------

    experience_score = min(
        (float(experience) / 5) * 100,
        100
    )

    # --------------------------------------------------------
    # Final Score
    # --------------------------------------------------------

    final_score = (
        float(skill_score) * 0.40
        +
        float(semantic_score) * 0.30
        +
        experience_score * 0.15
        +
        float(project_score) * 0.15
    )

    return round(
        min(max(final_score, 0), 100),
        2
    )


# ============================================================
# CANDIDATE RANK
# ============================================================

def get_candidate_rank(score):

    score = float(score)

    if score >= 85:
        return "Excellent Candidate"

    elif score >= 75:
        return "Strong Candidate"

    elif score >= 65:
        return "Shortlisted"

    elif score >= 50:
        return "Review Required"

    else:
        return "Rejected"


# ============================================================
# RANK MULTIPLE CANDIDATES
# ============================================================

def rank_candidates(candidates):

    ranked_candidates = []

    for candidate in candidates:

        candidate = dict(candidate)

        score = float(
            candidate.get("final_score", 0)
        )

        candidate["ranking_score"] = round(
            score,
            2
        )

        candidate["ranking_status"] = (
            get_candidate_rank(score)
        )

        ranked_candidates.append(
            candidate
        )

    ranked_candidates.sort(
        key=lambda x: x["ranking_score"],
        reverse=True
    )

    for index, candidate in enumerate(
        ranked_candidates,
        start=1
    ):

        candidate["rank"] = index

    return ranked_candidates