# 🧠 Adaptive Diagnostic Engine
A **1D Adaptive Testing System** that estimates a student's ability in real-time using **Item Response Theory (IRT)** and generates a **personalized study plan** via the Anthropic Claude API.

---

## 🗂 Project Structure

```
adaptive-engine/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── core/
│   │   └── database.py          # MongoDB connection (Motor async driver)
│   ├── models/
│   │   └── schemas.py           # Pydantic models: Question, UserSession, DTOs
│   ├── routers/
│   │   ├── session.py           # /session/start, /next-question, /submit-answer, /study-plan
│   │   └── questions.py         # /questions (admin/debug)
│   └── services/
│       ├── adaptive.py          # IRT algorithm — ability update & question selection
│       ├── llm.py               # Anthropic API — personalized study plan generation
│       ├── session_service.py   # MongoDB CRUD for UserSession
│       └── question_service.py  # MongoDB CRUD for Questions
├── scripts/
│   └── seed_questions.py        # Seeds 20 GRE-style questions into MongoDB
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/adaptive-engine.git
cd adaptive-engine
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
MONGO_URI=mongodb://localhost:27017      # or your Atlas URI
DB_NAME=adaptive_engine
OPENAI_API_KEY=sk-...            
```

> ⚠️ **Make sure your MongoDB server is running** before attempting to seed. For a local installation start `mongod`, or use a valid Atlas URI.

### 5. Seed the question bank

```bash
python scripts/seed_questions.py
```

Expected output: `✅ Seeded 20 questions into 'adaptive_engine.questions'`

### 6. Run the server

```bash
uvicorn app.main:app --reload
```

API is live at: **http://localhost:8000**  
Swagger docs: **http://localhost:8000/docs**

---

## 📡 API Documentation

### Session Flow

```
POST /api/session/start        →  Get session_id
GET  /api/next-question        →  Get next adaptive question
POST /api/submit-answer        →  Submit answer, get updated ability score
GET  /api/study-plan           →  Get AI-generated study plan (after 10 questions)
```

---

### `POST /api/session/start`

Start a new adaptive test session.

**Request body:**
```json
{
  "max_questions": 10
}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "message": "Session started! You will be asked up to 10 questions."
}
```

---

### `GET /api/next-question?session_id={id}`

Returns the next question chosen by the IRT-based adaptive algorithm (maximum Fisher information at current ability θ).

**Response:**
```json
{
  "session_id": "...",
  "question_number": 1,
  "total_questions": 10,
  "question_id": "ALG002",
  "text": "What is the solution set of |2x - 4| ≤ 6?",
  "options": {"A": "x ≤ 5", "B": "-1 ≤ x ≤ 5", "C": "x ≥ -1", "D": "-5 ≤ x ≤ 1"},
  "topic": "Algebra",
  "difficulty": 0.5
}
```

---

### `POST /api/submit-answer`

Submit the student's answer and trigger an IRT ability update.

**Request body:**
```json
{
  "session_id": "...",
  "question_id": "ALG002",
  "selected_answer": "B"
}
```

**Response:**
```json
{
  "is_correct": true,
  "correct_answer": "B",
  "ability_score": 0.57,
  "questions_remaining": 9,
  "session_complete": false,
  "message": "Great job!"
}
```

---

### `GET /api/study-plan?session_id={id}`

Available only after the session is complete. Calls Claude API to generate a 3-step personalized study plan.

**Response:**
```json
{
  "session_id": "...",
  "ability_score": 0.62,
  "total_questions": 10,
  "correct_answers": 7,
  "accuracy": 0.7,
  "weak_topics": ["Vocabulary", "Statistics"],
  "study_plan": "**Step 1: ...**\n..."
}
```

---

### `GET /api/questions` *(admin/debug)*

Returns all seeded questions.

---

## 🧮 Adaptive Algorithm — How It Works

### Scale Mapping

Questions store difficulty as `[0.1, 1.0]` (human-readable). Before any IRT calculation, this is mapped to the IRT b-parameter scale using:

```
b = (difficulty - 0.55) × 6.0   →   range ≈ [-2.7, 2.7]
```

This ensures `P(θ = b) ≈ 0.5` (ignoring guessing) holds true — the mathematical definition of an IRT difficulty parameter. Without this mapping, the model silently produces incorrect probabilities.

### Model: 3-Parameter Logistic IRT (3PL)

The probability of a student with ability **θ** answering an item correctly is:

```
P(θ) = c + (1 - c) / (1 + exp(-a × (θ - b)))
```

| Parameter | Meaning | Range |
|-----------|---------|-------|
| **θ** (theta) | Student's latent ability | [-3, 3] |
| **b** | Item difficulty | [0.1, 1.0] → mapped to [-3, 3] |
| **a** | Discrimination (how sharply the item differentiates abilities) | ~1.0–1.5 |
| **c** | Guessing (lower asymptote) | 0.25 for 4-option MCQ |

### Ability Update (Gradient Ascent on Log-Likelihood)

After every response, we update θ using a gradient step weighted by the item's **Fisher information**:

```
gradient = a × (response - P(θ)) × (P(θ) - c) / (P(θ) × (1 - c))
step     = learning_rate × gradient × (1 + I(θ))
θ_new    = θ + step          (clamped to [-3, 3])
```

This is a simplified Expected A Posteriori (EAP) update that:
- Moves θ up when the student answers correctly
- Moves θ down when incorrect
- Scales the step by how informative the item was

### Question Selection (Maximum Fisher Information)

At each step, the system picks the question that **maximizes Fisher information** at the current θ:

```
I(θ) = a² × (P(θ) - c)² / [(1 - c)² × P(θ) × (1 - P(θ))]
```

This ensures each question is optimally targeted — not too easy, not too hard — making the estimate converge faster than random or sequential selection.

### Why This Is Better Than Simple Difficulty Jumping

A naive adaptive system would just go "correct → pick harder, incorrect → pick easier." This approach:
- Doesn't account for guessing
- Treats all difficulty jumps equally regardless of how informative an item is
- Converges slowly

The IRT approach provides a **mathematically grounded** estimate that converges to the true ability in fewer questions.

---

## 🤖 AI Log — How I Used AI Tools

### What AI Accelerated
- **Schema design:** Prompted Claude to evaluate the 3PL model parameters for a GRE context and suggest appropriate discrimination/guessing values per topic.
- **Question generation:** Used Claude to draft the 20 GRE-style questions with calibrated difficulty scores, then manually reviewed each for correctness and appropriate difficulty spread.
- **IRT implementation:** Used AI to validate the gradient ascent update formula against IRT literature and check edge cases (guessing boundary, clamping behavior).
- **Study plan prompt engineering:** Iterated on the LLM prompt structure to ensure the output was specific to weak topics, not generic.

### What AI Could Not Solve
- **MongoDB async driver edge cases:** Motor (async MongoDB driver) has subtle differences from PyMongo in how it handles cursors and sessions. The AI suggested synchronous patterns that had to be manually corrected.
- **IRT parameter calibration:** While AI helped with the formulas, the actual discrimination values for each question required domain judgment — AI's suggestions needed manual tuning to ensure the questions would differentiate ability levels meaningfully.
- **FastAPI lifecycle events:** The `@app.on_event("startup")` pattern required debugging that AI initially suggested incorrectly for newer FastAPI versions (deprecated syntax).
- **OpenAI client initialization:** The OpenAI SDK validates API keys on instantiation, so placeholder keys caused import-time crashes. Required lazy-loading pattern that AI didn't initially suggest.

### Key Takeaway
AI was most valuable for **boilerplate, validation, and iteration** (schemas, prompt refinement, formula checking). For **architectural decisions** and **domain-specific tuning** (which questions work at which difficulty, when to lazy-load clients), human judgment was essential.

---

## 📦 MongoDB Schema

### `questions` collection

```json
{
  "question_id": "ALG002",
  "text": "What is the solution set of |2x - 4| ≤ 6?",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "correct_answer": "B",
  "difficulty": 0.5,
  "topic": "Algebra",
  "tags": ["absolute value", "inequalities"],
  "discrimination": 1.3,
  "guessing": 0.25
}
```

### `user_sessions` collection

```json
{
  "session_id": "uuid",
  "ability_score": 0.62,
  "questions_asked": ["ALG002", "VOC001", "..."],
  "responses": [
    {
      "question_id": "ALG002",
      "topic": "Algebra",
      "difficulty": 0.5,
      "is_correct": true,
      "ability_before": 0.5,
      "ability_after": 0.57,
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ],
  "is_complete": false,
  "study_plan": null,
  "max_questions": 10,
  "created_at": "...",
  "updated_at": "..."
}
```

---

## 🧪 Quick Test (curl)

```bash
# 1. Start session
curl -X POST http://localhost:8000/api/session/start \
  -H "Content-Type: application/json" \
  -d '{"max_questions": 10}'

# 2. Get next question (replace SESSION_ID)
curl "http://localhost:8000/api/next-question?session_id=SESSION_ID"

# 3. Submit answer
curl -X POST http://localhost:8000/api/submit-answer \
  -H "Content-Type: application/json" \
  -d '{"session_id":"SESSION_ID","question_id":"ALG001","selected_answer":"B"}'

# 4. Get study plan (after 10 answers)
curl "http://localhost:8000/api/study-plan?session_id=SESSION_ID"
```
