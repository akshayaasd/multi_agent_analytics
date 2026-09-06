# IVR Call Log Analytics - Multi-Agent Architecture

## Overview
This project implements a multi-agent architecture for analyzing Interactive Voice Response (IVR) call logs. The pipeline runs automatically to ingest, analyze, visualize, and distribute call insights.

## Architecture

Based on the original design in `image.png`, the system consists of the following components:

### 1. Agents (Backend)
- **Table Agent:** Reads raw IVR logs from the S3 bucket as they land. Parses call records, validates them, deduplicates, and writes clean row-per-call data into a shared Postgres table.
- **Analysis Agent:** Queries the database for the period in question to compute summary numbers (call volume, AHT, containment rate, fallback rate, top intents, abandonment). Generates deeper insights and a plain-language narrative.
- **Visualization Agent:** Takes the Analysis agent's output and determines the best chart representation (e.g., line chart for volume, bar chart for intents). Renders it as an image file.
- **Email Agent:** Compiles the narrative summary and chart image into an HTML email. Distributes it to stakeholders and logs delivery status in Postgres.

### 2. Shared State
- **Postgres Database:** A shared database acting as the single source of truth for the cleaned data. Read and written by all agents.

### 3. Orchestrator
- **LangGraph Orchestrator:** Controls the pipeline execution, waiting for each stage to finish before passing control. Handles ad-hoc requests and potential retries.

## Directory Structure

* **`backend/`**: Contains the Python multi-agent pipeline powered by LangGraph. Includes agents, SQLite (mock Postgres) database models, and execution scripts.
* **`frontend/`**: Reserved for the web interface that will allow users to trigger ad-hoc analysis, view historical charts, and manage email lists.
* **`docs/`**: Documentation, architecture diagrams, and implementation plans.

## Current Progress
- [x] Initial scaffolding of the Backend
- [x] Implemented LangGraph Orchestrator (`main.py`)
- [x] Implemented Table, Analysis, Visualization, and Email agents.
- [x] Local mocked dependencies (SQLite instead of Postgres, local directory for S3).
- [x] Connect Analysis Agent to a live LLM (OpenAI/Anthropic) for dynamic narratives. (Implemented with Ollama and OpenAI toggle via .env)
- [x] Set up the Frontend dashboard (React/Next.js) for triggering on-demand graphs. (Implemented React/Vite Dashboard)
- [x] Migrate local mocks (SQLite -> Postgres, Local folder -> AWS S3). (Added PostgreSQL support with SQLite fallback, S3 migration skipped for now)
