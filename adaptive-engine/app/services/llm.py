import os
from openai import OpenAI
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

_client = None

def _get_client():
    """Lazy-load the OpenAI client on first use."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "sk-your-key-here":
            raise ValueError(
                "OPENAI_API_KEY is not set or is using the placeholder value. "
                "Please set a valid OpenAI API key in your .env file."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def generate_study_plan(
    ability_score: float,
    topic_breakdown: Dict[str, dict],
    weak_topics: List[str],
    total_questions: int,
    correct_answers: int,
) -> str:
    """
    Call OpenAI GPT-4o-mini to generate a personalized 3-step study plan
    based on the student's performance data.
    """
    accuracy = round(correct_answers / total_questions * 100, 1) if total_questions > 0 else 0

    topic_summary = "\n".join(
        f"  - {topic}: {stats['accuracy']*100:.0f}% accuracy "
        f"({stats['total_questions']} questions, avg difficulty {stats['avg_difficulty']})"
        for topic, stats in topic_breakdown.items()
    )

    weak_str = ", ".join(weak_topics) if weak_topics else "None identified (great performance!)"

    prompt = f"""You are an expert GRE tutor. A student just completed an adaptive diagnostic test.
Here is their performance data:

Overall Ability Score: {ability_score:.2f} / 1.00
Overall Accuracy: {accuracy}% ({correct_answers}/{total_questions} correct)

Topic Breakdown:
{topic_summary}

Weak Topics (accuracy < 60%): {weak_str}

Based on this data, generate a concise, actionable 3-step personalized study plan.
Each step should:
1. Target a specific weak area or skill gap
2. Include concrete study actions (e.g., specific practice types, resources)
3. Have a realistic time estimate

Format your response as:

**Step 1: [Title]**
[2-3 sentences of specific guidance]
Time: [X hours/days]

**Step 2: [Title]**
[2-3 sentences of specific guidance]
Time: [X hours/days]

**Step 3: [Title]**
[2-3 sentences of specific guidance]
Time: [X hours/days]

**Summary:** [1 sentence motivational close]

Be specific to the topics the student struggled with. Do not give generic advice."""

    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=800,
        messages=[
            {"role": "system", "content": "You are an expert GRE tutor who gives specific, actionable study advice."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content
