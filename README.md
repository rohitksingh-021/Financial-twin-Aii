# Financial Twin AI 🤖📊

Financial Twin AI transforms digital banking from a reactive, transactional utility into a proactive, intelligent, and autonomous wealth-building partner. By building a living digital twin of a user's financial profile, it forecasts trajectories, monitors financial stress, predicts life milestones, and guides users toward financial freedom.

---

## 🚀 Key Features

*   **Financial Digital Twin Engine**: Plot net worth projections (realistic, optimistic, pessimistic) up to 5-10 years.
*   **Financial Vitality Score™**: A multidimensional health metric (0-100) assessing liquidity, investment growth, protection, and risk.
*   **Wealth GPS™**: Goal planning with turn-by-turn navigation, alerting you when you fall behind and adjusting savings dynamically.
*   **What-If Scenario Simulator**: Simulate financial changes (e.g., job loss, property purchase, major SIP increments) to instantly see the multi-year impact.
*   **Stress Monitor**: Early warning indicator assessing EMI burdens, liquid runway, and critical risk alerts.
*   **Predictive Life Events**: ML-driven identification of major milestones (e.g., home purchase readiness) based on historical cash flow patterns.
*   **8-Agent AI Advisor**: Interactive conversational advisor featuring explanation logic, confidence scores, helpful thumbs up/down feedback, category quick actions, and markdown reports.

---

## 🛠️ Technology Stack

### Frontend
*   **Core**: Next.js 15+, React 19, TypeScript
*   **Animation**: Framer Motion (smooth micro-animations, spring easings)
*   **Charts**: Recharts (responsive gradient line-charts, radar charts)
*   **Styling**: Vanilla CSS Variables (Sleek Dark glassmorphism, responsive grids)
*   **Icons**: Lucide React

### Backend
*   **Framework**: FastAPI, Python 3.10+
*   **Server**: Uvicorn (ASGI)
*   **Models**: Pydantic v2
*   **Predictive Modeling**: Time-Series Trend Analysis & Categorization heuristics

---

## 📂 Folder Structure

```text
├── backend/
│   ├── main.py               # Application entry point & FastAPI setup
│   ├── requirements.txt      # Python dependencies
│   ├── engines/              # Core business engines (vitality, twin, gps, stress)
│   ├── routers/              # API router endpoints
│   ├── models/               # Pydantic validation schemas
│   ├── store/                # Local data storage mocks
│   └── seed/                 # Sample customer profile seeds
│
├── frontend/
│   ├── package.json          # Node.js dependencies
│   ├── src/
│   │   ├── app/              # Next.js App Router (Layouts & Pages)
│   │   ├── components/       # Reusable UI cards, sidebars, charts
│   │   └── lib/              # API connectors, mock data fallbacks, helper utilities
```

---

## ⚙️ Installation & Running Locally

Ensure you have **Python 3.10+** and **Node.js 18+** installed.

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server (port 8000)
uvicorn main:app --reload --port 8000
```
API Documentation will be available at: http://localhost:8000/docs

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install node dependencies
npm install

# Start Next.js dev server (port 3000)
npm run dev
```
Open http://localhost:3000 in your browser to view the application.

---

## 🧠 AI Agent Orchestration Details

The **AI Advisor** runs on a cooperative 8-agent framework:
1.  **AI Orchestrator**: Manages state, classifies user query intent.
2.  **Financial Analyst**: Resolves data queries on spending & portfolio asset classes.
3.  **Investment Strategist**: Suggests SIP modifications & optimal mutual funds.
4.  **Behavioral Coach**: Guides spending limits and tracks budget discipline.
5.  **Risk Manager**: Validates goals against debt levels and liquid runway.
6.  **Tax Advisor**: Optimizes HRA, Section 80C, 80D, and NPS allocations.
7.  **Goal Planner**: Generates Wealth GPS routes and down-payment targets.
8.  **Explainability Agent**: Injects confidence rates & data points backing the recommendation.
