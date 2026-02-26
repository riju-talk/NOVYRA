# NOVYRA — Adaptive AI Learning Infrastructure

[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Prisma](https://img.shields.io/badge/Prisma-3982CE?style=for-the-badge&logo=Prisma&logoColor=white)](https://prisma.io/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Python](https://img.shields.io/badge/Python_3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)

> **Not a chatbot. An infrastructure layer for personalised education.**
> NOVYRA is a graph-driven, rubric-aware, mastery-tracking AI learning engine built without LangChain — pure Gemini SDK, Neo4j, and deterministic structured reasoning.

---

## Architecture Overview

```
NOVYRA/
├── apps/
│   ├── app/                  # Next.js 14 App Router (frontend)
│   └── ai-agent/             # FastAPI AI Engine (backend, port 8000)
│       └── app/
│           ├── core/         # config, llm client, prompts
│           ├── schemas/      # Pydantic I/O contracts
│           ├── services/     # 5 reasoning engines
│           └── api/routes/   # HTTP endpoints
├── infrastructure/
│   └── docker-compose.yml    # Neo4j + AI Engine + Next.js
└── apps/app/prisma/
    └── schema.prisma         # PostgreSQL models incl. mastery & evaluation
```

---

## Core Engines

### 1. Knowledge Graph (Neo4j)

The brain. Every concept is a node, every dependency is an edge.

| Node label | Purpose |
|---|---|
| `Concept` | A learnable topic with domain and difficulty |
| `User` | A student |
| Relationship `PREREQUISITE_OF` | Concept A must be learned before B |
| Relationship `MASTERED_BY` | User has mastery score on a concept |

**Key functions** (`app/services/knowledge_graph_service.py`)

```python
await add_concept(name, description, domain, difficulty)
await link_prerequisite(concept, prerequisite)
await fetch_concept_context(concept)      # → prerequisites + related
await get_user_weak_nodes(user_id)        # → concepts below mastery threshold
await get_recommended_path(user_id, target_concept)  # → shortest prereq path
await record_mastery(user_id, concept, score)        # → updates MASTERED_BY edge
```

---

### 2. Structured Reasoning Engine

Not a chat completion. Every answer is validated JSON.

```json
{
  "concept": "Binary Search",
  "prerequisites": ["Arrays", "Divide and Conquer"],
  "stepwise_reasoning": ["Step 1: ...", "Step 2: ..."],
  "hint_ladder": ["Gentle hint", "Medium hint", "Direct hint"],
  "final_solution": "Complete explanation",
  "confidence_score": 0.92,
  "related_concepts": ["Linear Search", "Binary Search Tree"]
}
```

**Flow:** detect language → translate to English → fetch graph context → Gemini JSON call → Pydantic validation → translate back if needed

**Endpoint:** `POST /api/reasoning/ask`

```json
{ "question": "What is dynamic programming?", "user_id": "abc", "language": "en" }
```

---

### 3. Rubric-Aware Evaluation Engine

Score any student submission against a weighted rubric. Arithmetic is computed in Python — not trusted to the LLM.

**Endpoint:** `POST /api/evaluation/evaluate`

```json
{
  "submission": "Dynamic programming is a method for solving...",
  "rubric": {
    "criteria": [
      { "name": "Clarity",          "weight": 0.3 },
      { "name": "Concept Accuracy", "weight": 0.4 },
      { "name": "Depth",            "weight": 0.3 }
    ]
  }
}
```

**Response:**

```json
{
  "criterion_scores": [
    { "name": "Clarity", "weight": 0.3, "score": 0.85, "feedback": "..." }
  ],
  "weighted_total": 78.5,
  "grade_level": "Good",
  "improvement_plan": ["Add more examples", "Define terms formally"]
}
```

---

### 4. Mastery Tracking Engine

Per-user, per-concept mastery that decays with inactivity.

```
mastery = (correct_attempts / total_attempts) × confidence_weight
```

Confidence weight decreases with:
- Heavy hint usage (`−0.1 per hint`)
- Inactivity decay (`−0.02/day after 7 days`)

After each attempt the score is written to both in-memory store and the Neo4j `MASTERED_BY` edge.

| Endpoint | Action |
|---|---|
| `POST /api/mastery/attempt` | Record one attempt, get mastery delta + nudge |
| `GET  /api/mastery/profile/{user_id}` | Full mastery profile: weak/strong concepts, overall progress |

---

### 5. Multilingual Layer

All reasoning is performed in English internally. Input/output translation is transparent.

**Supported languages:** Hindi, Bengali, Tamil, Telugu, Gujarati, Marathi, Kannada, Malayalam, Punjabi, Urdu, French, German, Spanish, Chinese, Arabic, Japanese, Korean, Portuguese, Russian

**Flow:**
```
Input (any language)
    ↓ langdetect
    ↓ deep-translator → English
    ↓ Reasoning Engine (English)
    ↓ deep-translator → original language
Output (original language)
```

---

## API Reference

### AI Engine — `http://localhost:8000`

| Method | Path | Engine |
|---|---|---|
| `GET`  | `/health` | Health + Neo4j status |
| `GET`  | `/docs` | Interactive Swagger UI |
| `POST` | `/api/reasoning/ask` | Structured Reasoning |
| `POST` | `/api/evaluation/evaluate` | Rubric Evaluation |
| `POST` | `/api/mastery/attempt` | Mastery Update |
| `GET`  | `/api/mastery/profile/{user_id}` | Mastery Profile |
| `POST` | `/api/graph/concept` | Add Concept node |
| `POST` | `/api/graph/prerequisite` | Link prerequisite |
| `GET`  | `/api/graph/context/{concept}` | Concept context |
| `GET`  | `/api/graph/weak/{user_id}` | Weak nodes |
| `GET`  | `/api/graph/path/{user_id}/{concept}` | Learning path |
| `POST` | `/api/qa` | Legacy Q&A (proxied to reasoning engine) |
| `POST` | `/api/quiz` | Quiz generation |
| `POST` | `/api/flashcards` | Flashcard generation |
| `POST` | `/api/mindmap` | Mindmap generation |
| `POST` | `/api/documents` | Document upload |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 · TypeScript · TailwindCSS · Radix UI |
| Backend | FastAPI · Python 3.12 · Pydantic v2 |
| LLM | Google Gemini 1.5 Flash (direct SDK, no LangChain) |
| Knowledge Graph | Neo4j 5.20 Community (Bolt + APOC) |
| Relational DB | PostgreSQL via Prisma ORM |
| Translation | deep-translator + langdetect |
| Retry logic | tenacity |
| Containerisation | Docker Compose |

---

## Platform Features (Frontend)

- **Gamification** — XP, levels (Freshman → Sage), Entropy Coins, achievements, streaks, leaderboards
- **Communities** — subject-specific groups, moderation roles
- **Q&A** — rich text, LaTeX, code blocks, upvotes, comments
- **Mentorship programs**
- **Dark/Light theme**, fully responsive

---

## Getting Started

### Prerequisites

- Docker + Docker Compose
- Node.js 20+ and pnpm
- A [Google AI Studio](https://aistudio.google.com/) API key (free tier works)

### 1. Clone and configure

```bash
git clone https://github.com/your-org/novyra.git
cd novyra
cp .env.example .env
# Edit .env — set GOOGLE_API_KEY and DATABASE_URL at minimum
```

### 2. Start all services

```bash
# Starts: Neo4j, AI Engine, Next.js frontend
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5000 |
| AI Engine API | http://localhost:8000 |
| AI Engine Docs | http://localhost:8000/docs |
| Neo4j Browser | http://localhost:7474 |

Neo4j credentials: `neo4j` / `novyra_neo4j`

### 3. Run database migration

```bash
cd apps/app
npx prisma migrate dev --name novyra_init
```

### 4. Local development (without Docker)

**Frontend:**
```bash
cd apps/app
pnpm install
pnpm dev          # http://localhost:3000
```

**AI Engine:**
```bash
cd apps/ai-agent
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Neo4j** (required for graph features):
```bash
docker run -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/novyra_neo4j \
  neo4j:5.20-community
```

---

## Environment Variables

See [`.env.example`](.env.example) for the full list. Required variables:

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Gemini API key |
| `DATABASE_URL` | PostgreSQL connection string |
| `NEO4J_URI` | Bolt URI (default: `bolt://neo4j:7687`) |
| `NEO4J_PASSWORD` | Neo4j password (default: `novyra_neo4j`) |
| `NEXTAUTH_SECRET` | NextAuth signing secret |
| `NEXT_PUBLIC_AI_BACKEND_TOKEN` | Internal token for Next.js → AI Engine |

---

## Database Schema (Prisma)

New models added for the AI engines (on top of existing community/gamification models):

| Model | Purpose |
|---|---|
| `Concept` | Learnable topic node (mirrors Neo4j for relational queries) |
| `ConceptPrerequisite` | Prerequisite links |
| `ConceptAttempt` | Per-attempt audit log with mastery delta |
| `MasteryRecord` | Latest mastery score per user × concept |
| `RubricEvaluation` | Stored evaluation results |

---

## Contributing

Pull requests are welcome. For major changes, open an issue first.

---

## License

MIT