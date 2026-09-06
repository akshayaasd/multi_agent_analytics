# IVR Call Log Analytics

A full-stack, multi-agent AI application designed to analyze, visualize, and distribute insights from IVR (Interactive Voice Response) call logs.

## Project Structure

This repository is split into three main areas:

* **`/backend`**: The Python LangGraph pipeline. It contains all the agents (Table, Analysis, Viz, Email) and orchestrates the automated data flow. Uses local mocks (SQLite, local files) for development.
* **`/frontend`**: The React/TypeScript user interface. (Coming soon: A dashboard to view generated reports and trigger ad-hoc analysis workflows).
* **`/docs`**: Contains architectural diagrams and the detailed `implementation_plan.md`.

## Getting Started

### Backend Pipeline
To run the automated analysis pipeline locally:
```bash
cd backend
./run.sh
```
Check `backend/outputs/` for the generated charts and daily report HTML.

### Frontend Dashboard
To run the web interface locally:
```bash
cd frontend
npm install
npm run dev
```
