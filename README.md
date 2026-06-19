# 🧠 SoulMetrics Backend 

Welcome to the **SoulMetrics Backend** repository setup documentation. This project is a multi-output psychometric profiling engine app powered by a 15-input, 5-output machine learning configuration representing the full **OCEAN** personality framework (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism).

Below is the structured architectural design for the restructured Django project, incorporating asynchronous processing via Celery and Redis, rule-based static mapping, and comprehensive user history tracking.

---

## 📂 1. Repository Structure

To handle modular design principles cleanly within Django, the single monolithic directory is broken out into explicit domains of responsibility:

```text
soulmetrics-backend/
│
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
│
├── soulmetrics/
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── celery.py            <-- Celery initialization & broker setup
│   └── settings.py          <-- JWT, Celery, and Auth User configurations
│
└── api/
    ├── __init__.py
    ├── admin.py
    ├── apps.py              <-- Pre-loads the 15-input/5-output model into memory
    ├── models.py            <-- Normalized entity schemas (Separated text fields)
    ├── urls.py              <-- Router definitions matching modular sections
    ├── serializers.py       <-- Payload verification & formatting rules
    ├── views.py             <-- Viewsets handling business endpoints
    ├── tasks.py             <-- Background async analysis worker tasks (Celery + OpenAI)
    ├── utils.py             <-- Static dictionaries for the 3-Tier trait lookups
    │
    ├── ml_models/           
    │   └── best_model.pkl   <-- Refactored 15-input / 5-output ML model binary
    │
    ├── management/
    │   └── commands/
    │       └── load_questions.py <-- Database seeder for the 15 IPIP framework questions
    │
    └── templates/
        └── profile_export.html   <-- Clean HTML print layout tailored for WeasyPrint PDF

```

---

## 💾 2. Core Database Schema & Entities

The database structure relies on text separations and `JSONField` allocations to serve frontend chart components directly, optimizing screen space for mobile viewports.

### `CustomUser` (Auth Module)

* `id`: `integer pk`
* `username`: `string`
* `email`: `string`
* `password`: `string`
* `edad`: `integer`
* `ocupacion`: `string`

### `Question` (Questionnaire Module)

* `id`: `integer pk`
* `code`: `string` (e.g., `'EST1'`, `'AGR2'`)
* `text`: `string` (e.g., `"I have a rich vocabulary."`)
* `category`: `string` (Choices: `'O'`, `'C'`, `'E'`, `'A'`, `'N'`)

### `PredictionHistory` (Prediction Module)

* `id`: `integer pk`
* `user_id`: `integer` (Many-to-One FK to `CustomUser`)
* `answers_data`: `json` (The 15 raw inputs and response times)
* `predicted_scores`: `json` (The exact 5 framework output scores from the model)
* `trait_descriptions`: `json` (Text descriptions captured on test day)
* `graphics_data`: `json` (Immediate Radar chart mapping object)
* `created_at`: `timestamp`

### `PersonalityProfile` (Insights Module)

* `id`: `integer pk`
* `user_id`: `integer` (One-to-One FK to `CustomUser`)
* `ai_summary`: `string` (Text chunk covering general behavior)
* `ai_trends_analysis`: `string` (Text tracking variance across history)
* `ai_recommendation`: `string` (Strategic life/work actions from the AI)
* `first_test_scores`: `json` (Snapshot baseline of user's very first test)
* `latest_test_scores`: `json` (Snapshot baseline of user's most recent test)
* `historical_graphics_data`: `json` (Time-series multi-line timeline progression data)
* `total_tests_taken`: `integer`
* `updated_at`: `timestamp`

---

## 🛠️ 3. Main Requirements Modules Descriptions

### Authentication & Profile Module

Manages identity via secure JSON Web Tokens (JWT). It tracks foundational demographic statistics like age and occupation, which are critical for appending contextual variables to background LLM analysis jobs later.

### Questionnaire Module

Handles the rendering of the diagnostic test. Instead of generating arbitrary variants that would break your stubborn ML feature shapes, it pulls the fixed 15 framework items from the database and returns them randomly ordered via `random.shuffle()`. This ensures the model receives its exact expected features while keeping users engaged with a unique slide structure every test.

### Prediction & Diagnostics Module

Triggers immediate multivariate processing when a test is submitted. To eliminate user drop-off caused by latency, this module performs high-speed in-memory matrix inference. It couples the score arrays with a localized rule-based text lookup dictionary (`utils.py`) to serve instant reports without freezing the application threads for external API generation calls.

### Asynchronous AI Profiling Module

An automated analytical engine managed by a Celery worker pool and backed by a Redis broker. The worker aggregates the user's demographic fields and historical progression matrix, structures a cohesive prompt data contract, calls an external LLM to generate deep psychological insights, splits the text into distinct fields, and commits updates to the profile.

### Export & Reporting Module

Compiles data components into an printable executive dossier. It references historical profiles, builds comparison tables, and converts HTML directly into clean PDFs using WeasyPrint for download or physical distribution.

---

## 📡 4. Endpoint Registry

### Auth & Profile Module

* `POST /api/auth/register/`: Registers a new user account using username, email, password, age, and occupation.
* `POST /api/auth/login/`: Validates credentials and returns JWT Access and Refresh token pairs.
* `POST /api/auth/login/refresh/`: Accepts a refresh token to generate a new short-lived access token.
* `POST /api/auth/logout/`: Blacklists active refresh token chains.
* `GET /api/auth/profile/`: Retrieves demographic values (`edad`, `ocupacion`) for the current user.
* `PUT /api/auth/profile/`: Modifies the user's demographic metadata attributes.

### Questionnaire Module

* `GET /api/questions/`: Delivers the array of 15 targeted test items in a shuffled sequence order.

### Prediction & Diagnostics Module

* `POST /api/predict/`: Accepts the payload containing 15 question answers and response times. Runs inference on `best_model.pkl`, builds immediate graphic variables, pulls static definitions, creates history records, triggers the async task, and returns immediate analysis payload results.
* `GET /api/history/`: Provides a list of the user's past `PredictionHistory` records, sorted chronologically with pagination.

### Personality Insights Module

* `GET /api/profile/personality/`: Retrieves the user's holistic profile analysis, including text breakdowns and historical progression line parameters.
* `GET /api/profile/personality/export/`: Generates and exports a clean, comprehensive PDF dossier.

---

## 🎨 5. Mobile-Optimized JSON Response Contracts

### Assessment Completion Result Contract (`POST /api/predict/`)

```json
{
  "id": 1042,
  "user_id": 15,
  "created_at": "2026-06-13T14:30:00Z",
  "predicted_scores": {
    "Openness": 4.1,
    "Conscientiousness": 3.2,
    "Extraversion": 3.8,
    "Agreeableness": 4.5,
    "Neuroticism": 2.1
  },
  "trait_descriptions": {
    "Openness": "You are highly imaginative and open to new experiences.",
    "Conscientiousness": "You balance structure with flexibility well.",
    "Extraversion": "You draw energy from social interactions and groups.",
    "Agreeableness": "You are highly empathetic and prioritize group harmony.",
    "Neuroticism": "You are emotionally resilient and handle stress effectively."
  },
  "graphics_data": {
    "radar_chart": {
      "title": "Your OCEAN Personality Footprint",
      "labels": ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"],
      "datasets": [
        {
          "label": "Predicted Personality",
          "data": [4.1, 3.2, 3.8, 4.5, 2.1],
          "fill_color": "rgba(54, 162, 235, 0.2)"
        }
      ]
    }
  }
}

```

### Holistic Profile Contract (`GET /api/profile/personality/`)

```json
{
  "id": 88,
  "user_id": 15,
  "last_updated": "2026-06-13T14:35:12Z",
  "report_metadata": {
    "total_tests_taken": 4,
    "first_test_date": "2026-01-15T10:00:00Z",
    "days_active": 144,
    "primary_dominant_trait": "Agreeableness",
    "highest_variance_trait": "Extraversion"
  },
  "ai_conclusions": {
    "summary": "Your profile shows strong stability in Agreeableness, but a fascinating recent spike in Extraversion and Conscientiousness.",
    "trends_analysis": "As your Neuroticism dropped over the last 3 tests, your Extraversion naturally rose, suggesting you are feeling more confident in social settings.",
    "recommendation": "Leverage your high Openness to try a new hobby or project that requires teamwork."
  },
  "historical_baselines": {
    "first_test_scores": {
      "Openness": 3.8, "Conscientiousness": 3.1, "Extraversion": 3.1, "Agreeableness": 4.0, "Neuroticism": 3.5
    },
    "latest_test_scores": {
      "Openness": 4.1, "Conscientiousness": 3.2, "Extraversion": 3.8, "Agreeableness": 4.5, "Neuroticism": 2.1
    }
  },
  "graphics_data": {
    "line_chart": {
      "title": "Trait Evolution Timeline",
      "x_axis_labels": ["Jan 2026", "Mar 2026", "May 2026", "Jun 2026"],
      "datasets": [
        { "label": "Extraversion", "data": [3.1, 3.2, 3.6, 3.8], "color": "#FF6384" },
        { "label": "Neuroticism", "data": [3.5, 3.2, 2.6, 2.1], "color": "#36A2EB" },
        { "label": "Agreeableness", "data": [4.0, 4.2, 4.3, 4.5], "color": "#4BC0C0" },
        { "label": "Conscientiousness", "data": [3.1, 3.1, 3.2, 3.2], "color": "#FFCE56" },
        { "label": "Openness", "data": [3.8, 3.9, 4.0, 4.1], "color": "#9966FF" }
      ]
    },
    "comparison_radar_chart": {
      "title": "Baseline Shift (First vs. Latest)",
      "labels": ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"],
      "datasets": [
        {
          "label": "Initial Baseline (Jan 2026)",
          "data": [3.8, 3.1, 3.1, 4.0, 3.5],
          "fill_color": "rgba(201, 203, 207, 0.2)"
        },
        {
          "label": "Current Status (Jun 2026)",
          "data": [4.1, 3.2, 3.8, 4.5, 2.1],
          "fill_color": "rgba(54, 162, 235, 0.2)"
        }
      ]
    }
  }
}

```