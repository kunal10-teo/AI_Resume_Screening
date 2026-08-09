def rank_candidates(candidates):
    """
    Rank candidates from highest score to lowest score.

    Expected format:
    [
        {"name": "Rahul", "score": 85},
        {"name": "Aman", "score": 92}
    ]
    """

    ranked = []

    for candidate in candidates:

        try:
            score = float(candidate.get("score", 0))
        except:
            score = 0

        candidate["score"] = score

        ranked.append(candidate)

    ranked.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # Add ranking number
    for index, candidate in enumerate(ranked, start=1):
        candidate["rank"] = index

    return ranked