# AI Workforce Decision & Resource Allocation Agent

An AI-driven workforce management system that dynamically assigns tasks to employees based on skills, availability, workload, priority, SLA, location, and historical performance.

## 🚀 Key Features

- **Intelligent Task Allocation** – Assigns tasks using multi-factor AI scoring.
- **Dynamic Reallocation** – Reassigns tasks when employee availability changes.
- **Emergency Workforce Swap** – Handles critical tasks by rearranging existing assignments.
- **Dynamic Task Splitting** – Breaks large tasks into smaller subtasks and distributes them across employees.
- **SLA Early Warning** – Identifies tasks that may become delayed.
- **Skill Backup Monitoring** – Detects skills dependent on a single employee.
- **Explainable Decisions** – Shows the factors behind every allocation.
- **Workforce Health Dashboard** – Provides an overview of workforce availability and allocation status.

## 🛠️ Tech Stack

- Python
- Flask
- HTML
- CSS
- Jinja2

## ⚙️ Run Locally

```bash
git clone <repository-url>
cd AI04-Workforce-Decision-Resource-Allocation
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
