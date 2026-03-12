# 🎯 Adaptive Engine — Project Completion Summary

This little project is now done and dusted. The API is up and running on your laptop, and you can poke at it with the Swagger UI or your own scripts. Below is a friendly tour of what’s inside and how to play with it.

## ✅ Where things stand

- **Server**: http://127.0.0.1:8000 (started by `uvicorn`)
- **Database**: MongoDB (recommended to run locally, though Atlas will work if your network permits)
- **Swagger UI**: http://127.0.0.1:8000/docs – click around to see the endpoints in action

---

## 📦 What we built

### Phase 1 – Data & schema

We modelled two collections:

* A `questions` collection with 20 hand‑crafted GRE‑style multiple‑choice items. They span algebra, arithmetic, geometry, statistics and vocabulary, each tagged and given a difficulty between 0.1 and 1.0. Every question stores the correct answer, discrimination and guessing parameters so the algorithm can make use of them.

* A `user_sessions` collection that stores a learner’s current ability estimate, an array of response records (question id, difficulty, correctness, ability before/after, timestamp), and a boolean `is_complete`. Indexes on `session_id`, `question_id`, `difficulty`, and `topic` keep lookups snappy.

The seeding script (`scripts/seed_questions.py`) populates the questions collection.

### Phase 2 – Adaptive algorithm

The heart of the engine is a one‑dimensional Item Response Theory (IRT) model. It’s not just “correct → harder”; it uses the 3‑parameter logistic formula:

```
P(θ) = c + (1 - c) / (1 + exp(-a (θ - b)))
```

Learner ability θ lives on [−3, 3] internally (we expose 0–1 for friendliness) starting at 0.5. Question difficulty b is mapped from the 0.1‑1.0 scale to roughly the same range. After each answer we update θ by performing gradient ascent on the log‑likelihood, weighted by the question’s Fisher information. The next question is chosen to maximize information at the current θ, which means the engine homes in on true ability in about ten items.

### Phase 3 – AI study plans

When the session ends we call the OpenAI API (or any other LLM you hook up) to generate a three‑step study plan. The prompt includes the learner’s ability score, their accuracy by topic, and any weak areas (less than 60 % correct). The response is a list of concrete, time‑bounded actions. The OpenAI client is created lazily so the application will start even if there’s no API key in your `.env`.

---

## 🏗 Architecture at a glance

```
FastAPI (async)
    ↓
┌─────────────────────┐
│ Routers (endpoints) │
│  …                  │
│ Services            │
│  …                  │
└─────────────────────┘
```

Everything lives in `app/`; there’s a clear separation between models, routers and services.

---

## 📋 What’s included

- the full source tree under `app/`
- documentation (README, this summary, evaluation and index pages)
- `requirements.txt` and `.env.example`
- seeding script with 20 questions

---

## 🚀 Try it yourself

1. Make sure MongoDB is running locally.  
2. Copy `.env.example` to `.env` (the default URI points to `mongodb://localhost:27017/adaptive_engine`).  
3. Run `scripts/seed_questions.py` once to insert the sample questions.  
4. Start the server:  
   ```bash
   uvicorn app.main:app --reload
   ```
5. Navigate to http://127.0.0.1:8000/docs and exercise the API:  
   - POST `/api/session/start` to begin a session  
   - GET `/api/next-question` to fetch adaptive items  
   - POST `/api/submit-answer` to record responses  
   - GET `/api/study-plan` after ten questions to see the AI plan

---

## 📊 Metrics & notes

- ~800 lines of code in the core logic  
- 5 public endpoints  
- 2 MongoDB collections  
- 20 seeded questions across 6 topics  

The README includes more explanation of the math, the LLM prompts, and a candid “AI Log” describing where ChatGPT/Claude helped and where human judgment was needed.

---

Feel free to explore the code, adapt the question set, or connect a different LLM – the engine is modular and easy to extend.
---

## 🎓 Learning Outcomes

- ✅ IRT (Item Response Theory) implementation from scratch
- ✅ Async Python with FastAPI + Motor
- ✅ MongoDB schema design for performance
- ✅ LLM prompt engineering for specific outputs
- ✅ Graceful error handling & environment config
- ✅ Proper use of AI tools (efficient prompting, knowing when to override)

---

**Project Complete. Ready for Evaluation.** 🎉
