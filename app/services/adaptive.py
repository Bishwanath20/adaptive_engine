"""
Adaptive Algorithm — 1D Item Response Theory (IRT)

Uses the 3-Parameter Logistic (3PL) model:

    P(θ) = c + (1 - c) / (1 + exp(-a * (θ - b)))

Where:
    θ (theta) = student's ability score        [-3, 3], mapped to [0, 1]
    b         = item difficulty parameter      (0.1 to 1.0 in our scale)
    a         = item discrimination parameter  (how well item separates abilities)
    c         = guessing parameter             (lower bound probability)

Ability Update (EAP - Expected A Posteriori simplified):
    After each response, we update θ using a gradient step toward the
    MLE estimate, scaled by the item's information value.
"""

import math
from typing import List, Optional
from app.models.schemas import ResponseRecord


# ── Scale helpers ─────────────────────────────────────────────────────────────

def difficulty_to_theta_scale(difficulty: float) -> float:
    """
    Map stored difficulty [0.1, 1.0] → IRT b-parameter [-2.4, 2.4].
    Keeps the difficulty parameter on the same scale as theta so that
    P(θ=b) = 0.5 (ignoring guessing), which is the IRT definition.
    """
    return (difficulty - 0.55) * 6.0


# ── IRT core functions ────────────────────────────────────────────────────────

def probability_correct(theta: float, difficulty: float, discrimination: float, guessing: float) -> float:
    """
    3PL IRT probability of a correct response.
    difficulty is converted from [0.1,1.0] storage scale to IRT b-parameter.
    """
    b = difficulty_to_theta_scale(difficulty)
    exponent = -discrimination * (theta - b)
    return guessing + (1 - guessing) / (1 + math.exp(exponent))


def item_information(theta: float, difficulty: float, discrimination: float, guessing: float) -> float:
    """
    Fisher information of an item at a given ability level.
    Higher information = item is more useful for estimating θ at this point.
    """
    p = probability_correct(theta, difficulty, discrimination, guessing)
    q = 1 - p
    if p <= guessing or q == 0:
        return 0.0
    return (discrimination ** 2) * ((p - guessing) ** 2) / ((1 - guessing) ** 2) * (q / p)


def update_ability(
    theta: float,
    is_correct: bool,
    difficulty: float,
    discrimination: float = 1.0,
    guessing: float = 0.25,
    learning_rate: float = 0.3,
) -> float:
    """
    Update ability score using a gradient ascent step on the log-likelihood.
    Clamps result to [-3, 3] range (standard IRT theta scale).
    """
    p = probability_correct(theta, difficulty, discrimination, guessing)
    response = 1 if is_correct else 0

    # Score function (derivative of log-likelihood)
    numerator = discrimination * (response - p) * (p - guessing)
    denominator = p * (1 - guessing)
    gradient = numerator / denominator if denominator != 0 else 0.0

    # Weight update by item information for stability
    info = item_information(theta, difficulty, discrimination, guessing)
    step = learning_rate * gradient * (1 + info)

    new_theta = theta + step
    return max(-3.0, min(3.0, new_theta))


def theta_to_display(theta: float) -> float:
    """Convert internal [-3,3] theta to a user-friendly [0,1] ability score."""
    return round((theta + 3) / 6, 3)


def display_to_theta(ability: float) -> float:
    """Convert user-facing [0,1] score back to internal [-3,3] theta."""
    return ability * 6 - 3


# ── Question selection ────────────────────────────────────────────────────────

def select_best_question(
    theta: float,
    candidate_questions: list,
    asked_ids: List[str],
) -> Optional[dict]:
    """
    Select the question with maximum Fisher information at current theta.
    Excludes already-asked questions.
    """
    candidates = [q for q in candidate_questions if q["question_id"] not in asked_ids]
    if not candidates:
        return None

    best_q = max(
        candidates,
        key=lambda q: item_information(
            theta,
            q["difficulty"],
            q.get("discrimination", 1.0),
            q.get("guessing", 0.25),
        ),
    )
    return best_q


# ── Performance analysis ──────────────────────────────────────────────────────

def analyze_performance(responses: List[ResponseRecord]) -> dict:
    """Compute per-topic accuracy and identify weak areas."""
    topic_stats: dict = {}

    for r in responses:
        topic = r.topic
        if topic not in topic_stats:
            topic_stats[topic] = {"correct": 0, "total": 0, "difficulties": []}
        topic_stats[topic]["total"] += 1
        topic_stats[topic]["difficulties"].append(r.difficulty)
        if r.is_correct:
            topic_stats[topic]["correct"] += 1

    analysis = {}
    for topic, stats in topic_stats.items():
        accuracy = stats["correct"] / stats["total"]
        analysis[topic] = {
            "accuracy": round(accuracy, 2),
            "total_questions": stats["total"],
            "avg_difficulty": round(sum(stats["difficulties"]) / len(stats["difficulties"]), 2),
        }

    weak_topics = [t for t, s in analysis.items() if s["accuracy"] < 0.6]
    return {"topic_breakdown": analysis, "weak_topics": weak_topics}
