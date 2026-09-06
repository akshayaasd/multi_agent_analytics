# Sentinel IVR Analytics - Multi-Agent Architecture

A full-stack, fully autonomous multi-agent AI application designed to analyze, visualize, and distribute insights from IVR (Interactive Voice Response) call logs.

## Architecture & Agents

This platform operates using a LangGraph-based multi-agent pipeline where specialized AI agents hand off work to one another:

1. **Orchestrator**: Coordinates the pipeline. Runs autonomously on a daily schedule (6:00 AM) or can be triggered ad-hoc via the web dashboard.
2. **Table Agent**: Ingests raw IVR logs, normalizes the data, and structures it into a relational database (Postgres/SQLite).
3. **Analysis Agent**: Queries the database to extract insights, identify intent trends, flag anomalies (like high fallback rates), and write a natural-language executive summary.
4. **Visualization Agent**: Takes the analysis and dynamically draws the appropriate charts (Intent Distributions, Call Dispositions, etc.) using matplotlib/seaborn.
5. **Email Agent**: Formats the final narrative and charts into a polished HTML email (with inline CID embedded images), autonomously sends it to stakeholders via the Resend API, and logs the delivery status.

## Project Structure

* **`/backend`**: The Python FastAPI server and LangGraph agent pipeline. Uses `APScheduler` for the automated 6:00 AM daily run.
* **`/frontend`**: The React/Vite dashboard where you can view recent data, review the artifacts archive, and manually trigger custom reports (Daily, Weekly, Monthly).
* **`/docs`**: Contains architectural diagrams (`image.png`) and the original `implementation_plan.md`.

## Setup & Environment Variables

### Backend Setup
1. Navigate to `/backend`.
2. Ensure you have your environment variables set in `backend/.env`:
   ```env
   # API Keys for the AI Agents
   OPENAI_API_KEY=your_openai_key
   
   # API Key for the Automated Email Agent
   RESEND_API_KEY=re_your_resend_key
   REPORT_RECIPIENT=your_email@domain.com
   ```
3. Run the application:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn api:app --reload
   ```
   *(Note: The background scheduler will automatically start with the server and queue the 6:00 AM daily report).*

### Frontend Setup
1. Navigate to `/frontend`.
2. Install dependencies and start the dev server:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Open `http://localhost:5174` in your browser.
