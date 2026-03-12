"""
Seed script: inserts 20 GRE-style questions into MongoDB.
Run with: python scripts/seed_questions.py
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "adaptive_engine")

QUESTIONS = [
    # ── Algebra (5 questions) ──────────────────────────────────────────────
    {
        "question_id": "ALG001",
        "text": "If 3x + 7 = 22, what is the value of x?",
        "options": {"A": "3", "B": "5", "C": "6", "D": "7"},
        "correct_answer": "B",
        "difficulty": 0.2,
        "topic": "Algebra",
        "tags": ["linear equations", "basic"],
        "discrimination": 1.2,
        "guessing": 0.25,
    },
    {
        "question_id": "ALG002",
        "text": "What is the solution set of |2x - 4| ≤ 6?",
        "options": {"A": "x ≤ 5", "B": "-1 ≤ x ≤ 5", "C": "x ≥ -1", "D": "-5 ≤ x ≤ 1"},
        "correct_answer": "B",
        "difficulty": 0.5,
        "topic": "Algebra",
        "tags": ["absolute value", "inequalities"],
        "discrimination": 1.3,
        "guessing": 0.25,
    },
    {
        "question_id": "ALG003",
        "text": "If f(x) = x² - 4x + 3, for what values of x does f(x) = 0?",
        "options": {"A": "x = 1, 3", "B": "x = -1, -3", "C": "x = 2, 4", "D": "x = 0, 3"},
        "correct_answer": "A",
        "difficulty": 0.4,
        "topic": "Algebra",
        "tags": ["quadratic", "factoring"],
        "discrimination": 1.4,
        "guessing": 0.25,
    },
    {
        "question_id": "ALG004",
        "text": "The sum of two numbers is 18 and their product is 56. What is the larger number?",
        "options": {"A": "12", "B": "14", "C": "10", "D": "8"},
        "correct_answer": "B",
        "difficulty": 0.6,
        "topic": "Algebra",
        "tags": ["word problems", "systems"],
        "discrimination": 1.3,
        "guessing": 0.25,
    },
    {
        "question_id": "ALG005",
        "text": "If log₂(x) + log₂(x-2) = 3, what is the value of x?",
        "options": {"A": "2", "B": "3", "C": "4", "D": "8"},
        "correct_answer": "C",
        "difficulty": 0.85,
        "topic": "Algebra",
        "tags": ["logarithms", "advanced"],
        "discrimination": 1.5,
        "guessing": 0.25,
    },

    # ── Arithmetic (4 questions) ──────────────────────────────────────────
    {
        "question_id": "ARI001",
        "text": "What is 15% of 240?",
        "options": {"A": "32", "B": "36", "C": "40", "D": "45"},
        "correct_answer": "B",
        "difficulty": 0.1,
        "topic": "Arithmetic",
        "tags": ["percentage", "basic"],
        "discrimination": 1.0,
        "guessing": 0.25,
    },
    {
        "question_id": "ARI002",
        "text": "A car travels 240 miles in 4 hours. At the same rate, how many miles will it travel in 7 hours?",
        "options": {"A": "380", "B": "400", "C": "420", "D": "440"},
        "correct_answer": "C",
        "difficulty": 0.25,
        "topic": "Arithmetic",
        "tags": ["rate", "proportion"],
        "discrimination": 1.1,
        "guessing": 0.25,
    },
    {
        "question_id": "ARI003",
        "text": "If an item costs $80 after a 20% discount, what was the original price?",
        "options": {"A": "$96", "B": "$100", "C": "$104", "D": "$110"},
        "correct_answer": "B",
        "difficulty": 0.45,
        "topic": "Arithmetic",
        "tags": ["discount", "reverse percentage"],
        "discrimination": 1.2,
        "guessing": 0.25,
    },
    {
        "question_id": "ARI004",
        "text": "The ratio of boys to girls in a class is 3:5. If there are 40 students total, how many are boys?",
        "options": {"A": "12", "B": "15", "C": "24", "D": "25"},
        "correct_answer": "B",
        "difficulty": 0.35,
        "topic": "Arithmetic",
        "tags": ["ratio", "proportion"],
        "discrimination": 1.2,
        "guessing": 0.25,
    },

    # ── Geometry (4 questions) ────────────────────────────────────────────
    {
        "question_id": "GEO001",
        "text": "What is the area of a circle with diameter 10?",
        "options": {"A": "25π", "B": "50π", "C": "100π", "D": "10π"},
        "correct_answer": "A",
        "difficulty": 0.3,
        "topic": "Geometry",
        "tags": ["circle", "area"],
        "discrimination": 1.2,
        "guessing": 0.25,
    },
    {
        "question_id": "GEO002",
        "text": "In a right triangle, the two legs have lengths 6 and 8. What is the length of the hypotenuse?",
        "options": {"A": "9", "B": "10", "C": "12", "D": "14"},
        "correct_answer": "B",
        "difficulty": 0.25,
        "topic": "Geometry",
        "tags": ["Pythagorean theorem", "right triangle"],
        "discrimination": 1.1,
        "guessing": 0.25,
    },
    {
        "question_id": "GEO003",
        "text": "A rectangular box has dimensions 3 × 4 × 5. What is its surface area?",
        "options": {"A": "60", "B": "82", "C": "94", "D": "120"},
        "correct_answer": "C",
        "difficulty": 0.6,
        "topic": "Geometry",
        "tags": ["surface area", "3D shapes"],
        "discrimination": 1.3,
        "guessing": 0.25,
    },
    {
        "question_id": "GEO004",
        "text": "Two parallel lines are cut by a transversal. If one interior angle is 65°, what is the co-interior (same-side interior) angle?",
        "options": {"A": "65°", "B": "90°", "C": "115°", "D": "125°"},
        "correct_answer": "C",
        "difficulty": 0.55,
        "topic": "Geometry",
        "tags": ["parallel lines", "transversal", "angles"],
        "discrimination": 1.3,
        "guessing": 0.25,
    },

    # ── Statistics (3 questions) ──────────────────────────────────────────
    {
        "question_id": "STA001",
        "text": "The scores of 5 students are: 70, 80, 90, 60, 100. What is the standard deviation (approx)?",
        "options": {"A": "12.4", "B": "14.1", "C": "15.8", "D": "16.7"},
        "correct_answer": "C",
        "difficulty": 0.75,
        "topic": "Statistics",
        "tags": ["standard deviation", "data analysis"],
        "discrimination": 1.4,
        "guessing": 0.25,
    },
    {
        "question_id": "STA002",
        "text": "The median of seven consecutive integers is 14. What is the largest of the seven?",
        "options": {"A": "16", "B": "17", "C": "18", "D": "19"},
        "correct_answer": "B",
        "difficulty": 0.4,
        "topic": "Statistics",
        "tags": ["median", "consecutive integers"],
        "discrimination": 1.2,
        "guessing": 0.25,
    },
    {
        "question_id": "STA003",
        "text": "A bag contains 4 red, 3 blue, and 5 green marbles. If one marble is drawn at random, what is the probability it is NOT green?",
        "options": {"A": "5/12", "B": "7/12", "C": "1/2", "D": "2/3"},
        "correct_answer": "B",
        "difficulty": 0.35,
        "topic": "Statistics",
        "tags": ["probability", "complementary events"],
        "discrimination": 1.2,
        "guessing": 0.25,
    },

    # ── Vocabulary (4 questions) ──────────────────────────────────────────
    {
        "question_id": "VOC001",
        "text": "Choose the word closest in meaning to EPHEMERAL:",
        "options": {"A": "Permanent", "B": "Transient", "C": "Ancient", "D": "Vibrant"},
        "correct_answer": "B",
        "difficulty": 0.3,
        "topic": "Vocabulary",
        "tags": ["synonyms", "GRE words"],
        "discrimination": 1.1,
        "guessing": 0.25,
    },
    {
        "question_id": "VOC002",
        "text": "Choose the word most opposite in meaning to LOQUACIOUS:",
        "options": {"A": "Verbose", "B": "Gregarious", "C": "Taciturn", "D": "Eloquent"},
        "correct_answer": "C",
        "difficulty": 0.65,
        "topic": "Vocabulary",
        "tags": ["antonyms", "GRE words"],
        "discrimination": 1.3,
        "guessing": 0.25,
    },
    {
        "question_id": "VOC003",
        "text": "The professor's argument was so ______ that even experts struggled to follow it.\nChoose the best word:",
        "options": {"A": "lucid", "B": "abstruse", "C": "coherent", "D": "trivial"},
        "correct_answer": "B",
        "difficulty": 0.8,
        "topic": "Vocabulary",
        "tags": ["sentence completion", "advanced vocabulary"],
        "discrimination": 1.4,
        "guessing": 0.25,
    },
    {
        "question_id": "VOC004",
        "text": "Which word best describes someone who is PARSIMONIOUS?",
        "options": {"A": "Generous", "B": "Miserly", "C": "Pompous", "D": "Reckless"},
        "correct_answer": "B",
        "difficulty": 0.55,
        "topic": "Vocabulary",
        "tags": ["word meaning", "character traits"],
        "discrimination": 1.2,
        "guessing": 0.25,
    },
]


async def seed():
    client = AsyncIOMotorClient(MONGO_URI)

    # quick connectivity check
    try:
        # ping will raise if we cannot connect to the server
        await client.admin.command("ping")
    except Exception as exc:
        print(
            "❌ Could not connect to MongoDB."
            f" Please ensure the database is running and MONGO_URI is correct."
            f"\nError: {exc}"
        )
        client.close()
        return

    db = client[DB_NAME]
    collection = db["questions"]

    try:
        existing = await collection.count_documents({})
    except Exception as exc:
        print("❌ Failed to query MongoDB collection:", exc)
        client.close()
        return

    if existing >= len(QUESTIONS):
        print(f"✅ Questions already seeded ({existing} found). Skipping.")
        client.close()
        return

    await collection.drop()
    await collection.insert_many(QUESTIONS)
    await collection.create_index("question_id", unique=True)

    count = await collection.count_documents({})
    print(f"✅ Seeded {count} questions into '{DB_NAME}.questions'")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
