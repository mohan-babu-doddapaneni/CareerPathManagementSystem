# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Django-based Career Path Recommendation System that combines web development with machine learning to parse resumes, identify skill gaps, and recommend career paths.

## Commands

### Setup
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Run Development Server
```bash
python manage.py runserver
```

### Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### Tests
```bash
python manage.py test
```
Note: The project currently has no implemented test cases in `webapp/tests.py`.

## Architecture

**Structure:** Monolithic Django app — all logic lives in the single `webapp/` app. No REST API; views render HTML templates directly.

**Key modules:**
- `webapp/views.py` — All view functions (~800 lines); handles auth, resume upload, career analysis, ML training, and admin
- `webapp/models.py` — 8 models: `Users` (custom auth, not Django's built-in), `WorkExperience`, `Resumes`, `Resume_skills`, `Resume_education`, `Resume_experience`, `SkillsDataset`, `Performance`, `Dataset`
- `webapp/Classification.py` — ML pipeline using sklearn; trains RandomForest/SVM/NaiveBayes/NeuralNet classifiers on `career_path_dataset.csv`
- `webapp/resume_parser.py` — Extracts email, phone, skills, education from `.docx` files using python-docx + spacy + regex
- `webapp/parse_exp.py` — Extracts years of experience and work history from resume text
- `webapp/Graphs.py` — Generates matplotlib accuracy/precision/recall/F1 plots saved to `webapp/static/assets/images/`
- `webapp/t.py` — Predefined skills list used for resume skill matching

**Data flow:**
1. User uploads `.docx` resume → parsed by `resume_parser.py` + `parse_exp.py`
2. Extracted skills stored in `Resume_skills` model
3. Skill gap analysis compares user skills vs. `SkillsDataset.csv` for target role
4. ML classifiers (trained on `career_path_dataset.csv`) predict suitable job titles

**Authentication:** Custom `Users` model with MD5-hashed passwords (not Django's built-in auth). Session-based login using `request.session['username']`.

**Database:** Configured via `DATABASE_URL` environment variable (uses `dj_database_url`). Falls back to SQLite if not set.

**Static files:** Served via WhiteNoise in production. Generated graph images are written directly to `webapp/static/assets/images/`.

**Deployment:** Configured for Vercel (`vercel.json`) and Render (`.onrender.com` in ALLOWED_HOSTS).

## Environment Variables

- `DATABASE_URL` — Database connection string (required for non-SQLite databases)
- `SECRET_KEY` — Django secret key (currently hardcoded in `settings.py` — do not use in production as-is)
