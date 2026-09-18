from flask import Flask, render_template_string, request, redirect, url_for
from copy import deepcopy
from datetime import datetime
import math

app = Flask(__name__)

# ============================================================
# AI-04
# AI WORKFORCE DECISION & RESOURCE ALLOCATION AGENT
#
# COMPLETE PIPELINE
#
# Workforce Data
#       ↓
# Task Intake
#       ↓
# AI Scoring Engine
#       ↓
# Initial Allocation
#       ↓
# Live Change Detection
#       ↓
# Emergency Reallocation / Swap Chain
#       ↓
# Dynamic Task Splitting
#       ↓
# SLA Early Warning
#       ↓
# Skill Backup Analysis
#       ↓
# Final Decision Dashboard
# ============================================================


# ============================================================
# 1. EMPLOYEE DATA
# ============================================================

employees = [
    {
        "name": "Arun",
        "skills": ["Networking", "Linux"],
        "workload": 40,
        "available": True,
        "location": "Chennai",
        "performance": 90
    },
    {
        "name": "Priya",
        "skills": ["Python", "SQL"],
        "workload": 30,
        "available": True,
        "location": "Chennai",
        "performance": 88
    },
    {
        "name": "Ravi",
        "skills": ["Networking", "Python"],
        "workload": 60,
        "available": True,
        "location": "Bangalore",
        "performance": 85
    },
    {
        "name": "Divya",
        "skills": ["SQL", "Database"],
        "workload": 20,
        "available": True,
        "location": "Chennai",
        "performance": 92
    }
]


# ============================================================
# 2. TASK DATA
# ============================================================

tasks = [
    {
        "name": "Server Failure",
        "skill": "Networking",
        "priority": "Critical",
        "sla": 1,
        "location": "Chennai",
        "estimated_hours": 1
    },
    {
        "name": "Database Error",
        "skill": "SQL",
        "priority": "High",
        "sla": 2,
        "location": "Chennai",
        "estimated_hours": 2
    },
    {
        "name": "Website Bug",
        "skill": "Python",
        "priority": "Medium",
        "sla": 5,
        "location": "Chennai",
        "estimated_hours": 4
    }
]


# ============================================================
# 3. RUNTIME STATE
# ============================================================

emergency_task = None
split_task_data = None

# Store last computed allocation
last_assignments = []


# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================

def get_employee(name):
    for employee in employees:
        if employee["name"] == name:
            return employee

    return None


def get_task(name):
    for task in tasks:
        if task["name"] == name:
            return task

    if emergency_task and emergency_task["name"] == name:
        return emergency_task

    return None


def priority_value(priority):
    values = {
        "Critical": 100,
        "High": 80,
        "Medium": 60,
        "Low": 40
    }

    return values.get(priority, 40)


# ============================================================
# 5. AI SCORING ENGINE
# ============================================================

def calculate_score(employee, task, current_workload=None):

    workload = (
        current_workload
        if current_workload is not None
        else employee["workload"]
    )

    # ----------------------------
    # Skill Match
    # ----------------------------

    if task["skill"] in employee["skills"]:
        skill_score = 100
    else:
        skill_score = 0

    # ----------------------------
    # Availability
    # ----------------------------

    availability_score = 100 if employee["available"] else 0

    # ----------------------------
    # Workload
    # ----------------------------

    workload_score = max(0, 100 - workload)

    # ----------------------------
    # Priority
    # ----------------------------

    priority_score = priority_value(task["priority"])

    # ----------------------------
    # Location
    # ----------------------------

    if employee["location"] == task["location"]:
        location_score = 100
    else:
        location_score = 50

    # ----------------------------
    # Performance
    # ----------------------------

    performance_score = employee["performance"]

    # ----------------------------
    # Final AI Score
    # ----------------------------

    score = (
        skill_score * 0.30 +
        availability_score * 0.20 +
        workload_score * 0.15 +
        priority_score * 0.15 +
        performance_score * 0.10 +
        location_score * 0.10
    )

    return round(score, 2)


# ============================================================
# 6. EXPLAINABLE AI
# ============================================================

def explain_decision(employee, task, workload):

    reasons = []

    if task["skill"] in employee["skills"]:
        reasons.append("Required skill matched")

    if employee["available"]:
        reasons.append("Employee is available")

    if workload <= 40:
        reasons.append("Low current workload")

    elif workload <= 70:
        reasons.append("Moderate current workload")

    else:
        reasons.append("High current workload")

    if employee["location"] == task["location"]:
        reasons.append("Same task location")

    if employee["performance"] >= 90:
        reasons.append("Strong historical performance")

    elif employee["performance"] >= 80:
        reasons.append("Good historical performance")

    if task["priority"] == "Critical":
        reasons.append("Critical priority considered")

    elif task["priority"] == "High":
        reasons.append("High priority considered")

    return reasons


# ============================================================
# 7. NORMAL ALLOCATION ENGINE
# ============================================================

def allocate_task_list(task_list):

    assignments = []

    current_workload = {
        employee["name"]: employee["workload"]
        for employee in employees
    }

    for task in task_list:

        best_employee = None
        best_score = -1
        best_reasons = []

        for employee in employees:

            if not employee["available"]:
                continue

            workload = current_workload[employee["name"]]

            score = calculate_score(
                employee,
                task,
                workload
            )

            if score > best_score:

                best_score = score
                best_employee = employee
                best_reasons = explain_decision(
                    employee,
                    task,
                    workload
                )

        if best_employee:

            employee_name = best_employee["name"]

            assignments.append({
                "task": task["name"],
                "employee": employee_name,
                "score": best_score,
                "reasons": best_reasons,
                "priority": task["priority"],
                "sla": task["sla"]
            })

            # Simulate additional workload
            current_workload[employee_name] += 10

        else:

            assignments.append({
                "task": task["name"],
                "employee": "Unassigned",
                "score": 0,
                "reasons": ["No suitable available employee"],
                "priority": task["priority"],
                "sla": task["sla"]
            })

    return assignments


def allocate_tasks():

    all_tasks = deepcopy(tasks)

    if emergency_task:
        all_tasks.append(deepcopy(emergency_task))

    return allocate_task_list(all_tasks)


# ============================================================
# 8. SLA RISK / EARLY WARNING
# ============================================================

def calculate_sla_risk(task, employee_name):

    if employee_name == "Unassigned":
        return {
            "risk": "Critical",
            "percentage": 100,
            "message": "No employee is currently assigned."
        }

    employee = get_employee(employee_name)

    if not employee:
        return {
            "risk": "Critical",
            "percentage": 100,
            "message": "Assigned employee not found."
        }

    workload = employee["workload"]

    # Base risk
    risk = 20

    # High workload increases risk
    if workload >= 80:
        risk += 45
    elif workload >= 60:
        risk += 30
    elif workload >= 40:
        risk += 15

    # Critical / high priority
    if task["priority"] == "Critical":
        risk += 15
    elif task["priority"] == "High":
        risk += 10

    # Location mismatch
    if employee["location"] != task["location"]:
        risk += 10

    # SLA pressure
    if task["sla"] <= 1:
        risk += 10
    elif task["sla"] <= 2:
        risk += 5

    risk = min(100, risk)

    if risk >= 75:
        level = "Critical"
        message = "Immediate intervention recommended."
    elif risk >= 50:
        level = "High"
        message = "Task may become delayed."
    elif risk >= 30:
        level = "Medium"
        message = "Monitor workload and SLA."
    else:
        level = "Low"
        message = "Task currently appears stable."

    return {
        "risk": level,
        "percentage": risk,
        "message": message
    }


def generate_early_warnings(assignments):

    warnings = []

    for assignment in assignments:

        task = get_task(assignment["task"])

        if not task:
            continue

        result = calculate_sla_risk(
            task,
            assignment["employee"]
        )

        warnings.append({
            "task": assignment["task"],
            "employee": assignment["employee"],
            "risk": result["risk"],
            "percentage": result["percentage"],
            "message": result["message"]
        })

    return warnings


# ============================================================
# 9. SKILL BACKUP ALERT
# ============================================================

def generate_skill_backup_alerts():

    skill_map = {}

    for employee in employees:

        for skill in employee["skills"]:

            if skill not in skill_map:
                skill_map[skill] = []

            skill_map[skill].append(employee["name"])

    alerts = []

    for skill, people in skill_map.items():

        if len(people) == 1:

            alerts.append({
                "skill": skill,
                "employee": people[0],
                "status": "Single Point of Dependency",
                "message": (
                    f"Only {people[0]} currently has this skill. "
                    "Cross-training or backup assignment is recommended."
                )
            })

        else:

            alerts.append({
                "skill": skill,
                "employee": ", ".join(people),
                "status": "Backup Available",
                "message": (
                    f"{len(people)} employees can currently support this skill."
                )
            })

    return alerts


# ============================================================
# 10. EMERGENCY TASK
# ============================================================

def create_emergency_task():

    return {
        "name": "Network Emergency",
        "skill": "Networking",
        "priority": "Critical",
        "sla": 1,
        "location": "Chennai",
        "estimated_hours": 1,
        "emergency": True
    }


# ============================================================
# 11. TASK CHAIN REALLOCATION
#
# Innovation:
#
# New Emergency Task
#        ↓
# Find best employee
#        ↓
# Employee already handling task?
#        ↓
# Find replacement for old task
#        ↓
# Move old task
#        ↓
# Give best employee the emergency
#
# ============================================================

def calculate_emergency_reallocation():

    if not emergency_task:
        return None

    base_tasks = deepcopy(tasks)

    # ----------------------------------------
    # Step 1: Find best employee for emergency
    # ----------------------------------------

    best_employee = None
    best_score = -1

    current_workload = {
        employee["name"]: employee["workload"]
        for employee in employees
    }

    for employee in employees:

        if not employee["available"]:
            continue

        score = calculate_score(
            employee,
            emergency_task,
            current_workload[employee["name"]]
        )

        if score > best_score:

            best_score = score
            best_employee = employee

    if not best_employee:
        return {
            "success": False,
            "message": "No available employee can handle the emergency.",
            "before": [],
            "after": []
        }

    # ----------------------------------------
    # Step 2: Normal allocation
    # ----------------------------------------

    before = allocate_task_list(base_tasks)

    emergency_employee = best_employee["name"]

    # ----------------------------------------
    # Step 3: Check if emergency employee
    # is already busy
    # ----------------------------------------

    existing_task = None

    for assignment in before:

        if assignment["employee"] == emergency_employee:
            existing_task = assignment
            break

    # ----------------------------------------
    # Case A:
    # Employee is free
    # ----------------------------------------

    if existing_task is None:

        after = deepcopy(before)

        after.append({
            "task": emergency_task["name"],
            "employee": emergency_employee,
            "score": best_score,
            "reallocated": False,
            "action": "Emergency assigned to available employee"
        })

        return {
            "success": True,
            "message": (
                f"{emergency_employee} was available and "
                "assigned directly to the emergency."
            ),
            "before": before,
            "after": after,
            "emergency_employee": emergency_employee,
            "displaced_task": None
        }

    # ----------------------------------------
    # Case B:
    # Employee is busy
    # ----------------------------------------

    displaced_task_name = existing_task["task"]

    displaced_task = get_task(displaced_task_name)

    replacement = None
    replacement_score = -1

    for employee in employees:

        if not employee["available"]:
            continue

        if employee["name"] == emergency_employee:
            continue

        score = calculate_score(
            employee,
            displaced_task,
            current_workload[employee["name"]]
        )

        if score > replacement_score:

            replacement_score = score
            replacement = employee

    # ----------------------------------------
    # No replacement
    # ----------------------------------------

    if replacement is None:

        return {
            "success": False,
            "message": (
                "Emergency detected, but the displaced task "
                "has no suitable replacement."
            ),
            "before": before,
            "after": before,
            "emergency_employee": emergency_employee,
            "displaced_task": displaced_task_name
        }

    # ----------------------------------------
    # Perform swap
    # ----------------------------------------

    after = []

    for assignment in before:

        if assignment["task"] == displaced_task_name:

            after.append({
                "task": displaced_task_name,
                "employee": replacement["name"],
                "score": replacement_score,
                "reallocated": True,
                "action": (
                    f"Moved from {emergency_employee} "
                    f"to {replacement['name']}"
                )
            })

        else:

            after.append({
                **assignment,
                "reallocated": False,
                "action": "No change"
            })

    # Add emergency assignment

    after.append({
        "task": emergency_task["name"],
        "employee": emergency_employee,
        "score": best_score,
        "reallocated": True,
        "action": (
            f"Emergency assigned to {emergency_employee}; "
            f"{displaced_task_name} moved to {replacement['name']}"
        )
    })

    return {
        "success": True,
        "message": (
            f"Emergency required {emergency_employee}. "
            f"The existing task '{displaced_task_name}' "
            f"was dynamically moved to {replacement['name']}."
        ),
        "before": before,
        "after": after,
        "emergency_employee": emergency_employee,
        "displaced_task": displaced_task_name,
        "replacement": replacement["name"]
    }


# ============================================================
# 12. DYNAMIC TASK SPLITTING
#
# Innovation:
#
# Large Task
#      ↓
# AI decomposes task
#      ↓
# Planning
# Development
# Database
# Testing
#      ↓
# Multiple employees
# ============================================================

def generate_subtasks(task):

    task_name = task["name"]

    subtasks = [
        {
            "name": f"{task_name} - Planning",
            "skill": "Python",
            "priority": task["priority"],
            "sla": task["sla"],
            "location": task["location"]
        },
        {
            "name": f"{task_name} - Development",
            "skill": "Python",
            "priority": task["priority"],
            "sla": task["sla"],
            "location": task["location"]
        },
        {
            "name": f"{task_name} - Database",
            "skill": "SQL",
            "priority": task["priority"],
            "sla": task["sla"],
            "location": task["location"]
        },
        {
            "name": f"{task_name} - Testing",
            "skill": "Linux",
            "priority": task["priority"],
            "sla": task["sla"],
            "location": task["location"]
        }
    ]

    return subtasks


def allocate_split_subtasks(subtasks):

    results = []

    current_workload = {
        employee["name"]: employee["workload"]
        for employee in employees
    }

    used_employees = set()

    for subtask in subtasks:

        candidates = []

        for employee in employees:

            if not employee["available"]:
                continue

            workload = current_workload[employee["name"]]

            score = calculate_score(
                employee,
                subtask,
                workload
            )

            # Strongly prefer employees not already used
            if employee["name"] not in used_employees:
                adjusted_score = score
            else:
                adjusted_score = score - 15

            candidates.append(
                (
                    adjusted_score,
                    score,
                    employee
                )
            )

        if not candidates:

            results.append({
                "task": subtask["name"],
                "skill": subtask["skill"],
                "employee": "Unassigned",
                "score": 0
            })

            continue

        candidates.sort(
            key=lambda x: x[0],
            reverse=True
        )

        adjusted_score, original_score, employee = candidates[0]

        employee_name = employee["name"]

        results.append({
            "task": subtask["name"],
            "skill": subtask["skill"],
            "employee": employee_name,
            "score": original_score
        })

        current_workload[employee_name] += 10
        used_employees.add(employee_name)

    return results


def calculate_task_splitting():

    if not split_task_data:
        return None

    task = split_task_data

    subtasks = generate_subtasks(task)

    allocation = allocate_split_subtasks(subtasks)

    return {
        "original_task": task["name"],
        "subtasks": subtasks,
        "allocation": allocation
    }


# ============================================================
# 13. WORKFORCE HEALTH
# ============================================================

def calculate_health(assignments):

    if not employees:
        return 0

    available_ratio = (
        sum(
            1
            for employee in employees
            if employee["available"]
        )
        / len(employees)
    )

    avg_workload = (
        sum(
            employee["workload"]
            for employee in employees
        )
        / len(employees)
    )

    workload_health = max(
        0,
        100 - avg_workload
    )

    assigned_ratio = 0

    if assignments:

        assigned_ratio = (
            sum(
                1
                for a in assignments
                if a["employee"] != "Unassigned"
            )
            / len(assignments)
        )

    health = (
        available_ratio * 40 +
        workload_health / 100 * 30 +
        assigned_ratio * 30
    )

    return round(health, 1)


# ============================================================
# 14. CURRENT SYSTEM STATUS
# ============================================================

def get_status_message(health):

    if health >= 75:
        return "Stable"

    if health >= 50:
        return "Moderate"

    return "Needs Attention"


# ============================================================
# 15. MAIN DASHBOARD
# ============================================================

@app.route("/")
def home():

    global last_assignments

    assignments = allocate_tasks()

    last_assignments = assignments

    warnings = generate_early_warnings(assignments)

    skill_alerts = generate_skill_backup_alerts()

    emergency_result = calculate_emergency_reallocation()

    split_result = calculate_task_splitting()

    health = calculate_health(assignments)

    critical_warnings = sum(
        1
        for warning in warnings
        if warning["risk"] == "Critical"
    )

    high_warnings = sum(
        1
        for warning in warnings
        if warning["risk"] == "High"
    )

    backup_risks = sum(
        1
        for alert in skill_alerts
        if alert["status"] == "Single Point of Dependency"
    )

    available = sum(
        1
        for employee in employees
        if employee["available"]
    )

    assigned = sum(
        1
        for assignment in assignments
        if assignment["employee"] != "Unassigned"
    )

    return render_template_string(
        HTML,

        employees=employees,
        tasks=tasks,
        assignments=assignments,

        warnings=warnings,
        skill_alerts=skill_alerts,

        emergency_task=emergency_task,
        emergency_result=emergency_result,

        split_task_data=split_task_data,
        split_result=split_result,

        health=health,
        status=get_status_message(health),

        available=available,
        assigned=assigned,

        critical_warnings=critical_warnings,
        high_warnings=high_warnings,
        backup_risks=backup_risks,

        now=datetime.now().strftime(
            "%d %b %Y • %I:%M:%S %p"
        )
    )


# ============================================================
# 16. CHANGE EMPLOYEE AVAILABILITY
# ============================================================

@app.route("/change_status", methods=["POST"])
def change_status():

    name = request.form.get("name")

    employee = get_employee(name)

    if employee:

        employee["available"] = not employee["available"]

    return redirect(url_for("home"))


# ============================================================
# 17. ADD EMERGENCY
# ============================================================

@app.route("/add_emergency", methods=["POST"])
def add_emergency():

    global emergency_task

    emergency_task = create_emergency_task()

    return redirect(url_for("home"))


# ============================================================
# 18. CLEAR EMERGENCY
# ============================================================

@app.route("/clear_emergency", methods=["POST"])
def clear_emergency():

    global emergency_task

    emergency_task = None

    return redirect(url_for("home"))


# ============================================================
# 19. SPLIT TASK
# ============================================================

@app.route("/split_task", methods=["POST"])
def split_task():

    global split_task_data

    task_name = request.form.get("task")

    selected_task = get_task(task_name)

    if selected_task:

        split_task_data = deepcopy(selected_task)

    return redirect(url_for("home"))


# ============================================================
# 20. CLEAR SPLIT
# ============================================================

@app.route("/clear_split", methods=["POST"])
def clear_split():

    global split_task_data

    split_task_data = None

    return redirect(url_for("home"))


# ============================================================
# 21. COMPLETE WEBSITE
# ============================================================

HTML = """

<!DOCTYPE html>

<html>

<head>

<title>
AI Workforce Decision & Resource Allocation Agent
</title>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<style>

/* =========================================================
   GLOBAL
========================================================= */

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    font-family:
        Inter,
        Arial,
        sans-serif;

    background:
        #f4f7fb;

    color:
        #172033;
}

a {
    text-decoration: none;
}

button,
select {

    font-family: inherit;
}


/* =========================================================
   HEADER
========================================================= */

.header {

    background:
        linear-gradient(
            135deg,
            #102a72,
            #1f4fbf
        );

    color: white;

    padding: 38px 5%;

    position: relative;

    overflow: hidden;
}

.header:after {

    content: "";

    position: absolute;

    width: 350px;
    height: 350px;

    border-radius: 50%;

    background:
        rgba(255,255,255,0.06);

    right: -100px;
    top: -150px;
}

.header-content {

    position: relative;

    z-index: 2;

    max-width: 1250px;

    margin: auto;
}

.header h1 {

    margin: 0;

    font-size: 36px;

    letter-spacing: -1px;
}

.header p {

    margin:
        10px 0 0;

    font-size: 16px;

    opacity: 0.9;
}

.live {

    display: inline-flex;

    align-items: center;

    gap: 8px;

    margin-top: 18px;

    padding:
        7px 12px;

    border-radius: 30px;

    background:
        rgba(255,255,255,0.12);

    font-size: 13px;
}

.dot {

    width: 9px;
    height: 9px;

    background: #55efc4;

    border-radius: 50%;
}


/* =========================================================
   CONTAINER
========================================================= */

.container {

    width: 92%;

    max-width: 1250px;

    margin:
        28px auto;
}


/* =========================================================
   PIPELINE
========================================================= */

.pipeline {

    display: grid;

    grid-template-columns:
        repeat(9, 1fr);

    gap: 6px;

    margin-bottom: 28px;
}

.pipeline-step {

    background: white;

    border-radius: 10px;

    padding: 12px 6px;

    text-align: center;

    border:
        1px solid #e2e8f0;

    font-size: 11px;

    font-weight: 700;

    color: #536174;

}

.pipeline-step.active {

    background: #eaf0ff;

    border-color: #a9bcf5;

    color: #1741a0;
}


/* =========================================================
   KPI
========================================================= */

.dashboard {

    display: grid;

    grid-template-columns:
        repeat(5, 1fr);

    gap: 16px;

    margin-bottom: 25px;
}

.card {

    background: white;

    padding: 21px;

    border-radius: 14px;

    border:
        1px solid #e3e8f0;

    box-shadow:
        0 4px 15px
        rgba(30,50,80,0.05);
}

.card .number {

    font-size: 30px;

    font-weight: 800;

    color: #1741a0;
}

.card .label {

    margin-top: 6px;

    color: #667085;

    font-size: 13px;
}


/* =========================================================
   SECTION
========================================================= */

.section {

    background: white;

    padding: 25px;

    margin-bottom: 24px;

    border-radius: 15px;

    border:
        1px solid #e2e8f0;

    box-shadow:
        0 4px 18px
        rgba(30,50,80,0.05);
}

.section-header {

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 20px;

    margin-bottom: 18px;
}

.section h2 {

    margin: 0;

    font-size: 21px;

    color: #152c62;
}

.section-description {

    color: #667085;

    font-size: 13px;

    margin-top: 6px;
}


/* =========================================================
   TABLE
========================================================= */

.table-wrapper {

    overflow-x: auto;
}

table {

    width: 100%;

    border-collapse:
        collapse;

    min-width: 700px;
}

th {

    background: #f1f5ff;

    color: #344054;

    font-size: 12px;

    text-transform:
        uppercase;

    letter-spacing:
        0.4px;
}

th,
td {

    padding: 13px;

    border-bottom:
        1px solid #edf0f5;

    text-align: left;

    font-size: 13px;
}


/* =========================================================
   BADGES
========================================================= */

.badge {

    display: inline-block;

    padding:
        5px 9px;

    border-radius: 20px;

    font-size: 11px;

    font-weight: 700;
}

.available {

    background: #e7f8ef;

    color: #16834b;
}

.unavailable {

    background: #ffe9e9;

    color: #c62828;
}

.critical {

    background: #ffe5e5;

    color: #c62828;
}

.high {

    background: #fff0db;

    color: #b86b00;
}

.medium {

    background: #fff8d9;

    color: #8a7300;
}

.low {

    background: #e9f7ee;

    color: #16834b;
}

.stable {

    background: #e7f8ef;

    color: #16834b;
}

.warning {

    background: #fff1db;

    color: #b86b00;
}


/* =========================================================
   BUTTONS
========================================================= */

button {

    border: none;

    padding:
        9px 13px;

    border-radius: 7px;

    cursor: pointer;

    background: #1741a0;

    color: white;

    font-weight: 600;

    font-size: 12px;
}

button:hover {

    opacity: 0.88;
}

.danger {

    background: #d93025;
}

.success {

    background: #16834b;
}

.dark {

    background: #26354d;
}

.outline {

    background: white;

    color: #1741a0;

    border:
        1px solid #b8c5df;
}


/* =========================================================
   SCORE
========================================================= */

.score {

    font-weight: 800;

    color: #1741a0;
}

.score-bar {

    width: 100px;

    height: 7px;

    background: #e8edf5;

    border-radius: 10px;

    overflow: hidden;

    display: inline-block;

    margin-right: 8px;
}

.score-fill {

    height: 100%;

    background: #315dcc;

}


/* =========================================================
   WORKFLOW
========================================================= */

.workflow {

    display: flex;

    align-items: center;

    justify-content: center;

    flex-wrap: wrap;

    gap: 8px;

    margin-top: 20px;
}

.workflow-box {

    background: #f5f7fb;

    border:
        1px solid #dce3ef;

    border-radius: 10px;

    padding:
        14px 17px;

    font-weight: 700;

    font-size: 12px;

    text-align: center;
}

.arrow {

    font-size: 21px;

    color: #315dcc;
}


/* =========================================================
   TWO COLUMN
========================================================= */

.two-column {

    display: grid;

    grid-template-columns:
        1fr 1fr;

    gap: 20px;
}


/* =========================================================
   INNOVATION
========================================================= */

.innovation {

    background:
        linear-gradient(
            135deg,
            #f8faff,
            #eef3ff
        );

    border:
        1px solid #cbd8f7;

    border-radius: 13px;

    padding: 20px;

    margin-top: 12px;
}

.innovation h3 {

    margin-top: 0;

    color: #173b8f;
}

.innovation p {

    color: #526071;

    font-size: 13px;

    line-height: 1.6;
}

.innovation-number {

    display: inline-flex;

    width: 32px;
    height: 32px;

    align-items: center;
    justify-content: center;

    border-radius: 50%;

    background: #173b8f;

    color: white;

    font-weight: 800;

    margin-right: 8px;
}


/* =========================================================
   EMERGENCY
========================================================= */

.emergency {

    border:
        2px solid #ef4444;

    background:
        #fff8f8;
}

.swap-flow {

    display: flex;

    align-items: center;

    justify-content: center;

    flex-wrap: wrap;

    gap: 12px;

    margin:
        18px 0;
}

.swap-card {

    padding: 14px;

    border-radius: 10px;

    background: white;

    border:
        1px solid #e2e8f0;

    text-align: center;

    min-width: 145px;

    font-size: 12px;
}


/* =========================================================
   WARNING
========================================================= */

.warning-card {

    border-left:
        5px solid #e3a008;

    background: #fffaf0;

    padding: 14px;

    border-radius: 8px;

    margin-bottom: 10px;
}

.critical-card {

    border-left:
        5px solid #d93025;

    background: #fff5f5;
}


/* =========================================================
   HEALTH
========================================================= */

.health {

    display: flex;

    align-items: center;

    gap: 20px;

    flex-wrap: wrap;
}

.health-circle {

    width: 100px;
    height: 100px;

    border-radius: 50%;

    border:
        10px solid #e7edf8;

    display: flex;

    align-items: center;
    justify-content: center;

    font-size: 22px;

    font-weight: 800;

    color: #173b8f;
}


/* =========================================================
   SELECT
========================================================= */

select {

    padding:
        10px 12px;

    border:
        1px solid #ccd5e5;

    border-radius: 7px;

    background: white;

    min-width: 220px;
}


/* =========================================================
   FOOTER
========================================================= */

.footer {

    text-align: center;

    padding: 30px;

    color: #7b8798;

    font-size: 12px;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media(max-width: 1000px) {

    .dashboard {

        grid-template-columns:
            repeat(2, 1fr);
    }

    .pipeline {

        grid-template-columns:
            repeat(3, 1fr);
    }

    .two-column {

        grid-template-columns: 1fr;
    }
}

@media(max-width: 600px) {

    .dashboard {

        grid-template-columns: 1fr;
    }

    .header h1 {

        font-size: 26px;
    }
}

</style>

</head>


<body>


<!-- =====================================================
     HEADER
===================================================== -->

<div class="header">

    <div class="header-content">

        <h1>
            AI Workforce Decision & Resource Allocation Agent
        </h1>

        <p>
            Dynamic workforce intelligence • Real-time allocation •
            Explainable AI • Disruption recovery
        </p>

        <div class="live">

            <span class="dot"></span>

            Live Decision Engine

            &nbsp;•&nbsp;

            {{ now }}

        </div>

    </div>

</div>


<div class="container">


<!-- =====================================================
     SYSTEM PIPELINE
===================================================== -->

<div class="pipeline">

    <div class="pipeline-step active">
        1. Workforce
    </div>

    <div class="pipeline-step active">
        2. Task Intake
    </div>

    <div class="pipeline-step active">
        3. AI Scoring
    </div>

    <div class="pipeline-step active">
        4. Allocation
    </div>

    <div class="pipeline-step active">
        5. Change Detection
    </div>

    <div class="pipeline-step active">
        6. Reallocation
    </div>

    <div class="pipeline-step active">
        7. Task Split
    </div>

    <div class="pipeline-step active">
        8. SLA Risk
    </div>

    <div class="pipeline-step active">
        9. Backup
    </div>

</div>


<!-- =====================================================
     KPI DASHBOARD
===================================================== -->

<div class="dashboard">

    <div class="card">

        <div class="number">
            {{ employees|length }}
        </div>

        <div class="label">
            Total Employees
        </div>

    </div>


    <div class="card">

        <div class="number">
            {{ tasks|length }}
        </div>

        <div class="label">
            Active Tasks
        </div>

    </div>


    <div class="card">

        <div class="number">
            {{ available }}
        </div>

        <div class="label">
            Available Resources
        </div>

    </div>


    <div class="card">

        <div class="number">
            {{ assigned }}
        </div>

        <div class="label">
            Assigned Tasks
        </div>

    </div>


    <div class="card">

        <div class="number">
            {{ health }}%
        </div>

        <div class="label">
            Workforce Health
        </div>

    </div>

</div>


<!-- =====================================================
     WORKFLOW EXPLANATION
===================================================== -->

<div class="section">

    <div class="section-header">

        <div>

            <h2>
                End-to-End AI Decision Pipeline
            </h2>

            <div class="section-description">

                The system continuously evaluates people, tasks,
                workload, urgency, SLA, location and performance.

            </div>

        </div>

    </div>


    <div class="workflow">

        <div class="workflow-box">
            Employee Data
        </div>

        <div class="arrow">→</div>

        <div class="workflow-box">
            Task Requirements
        </div>

        <div class="arrow">→</div>

        <div class="workflow-box">
            AI Scoring
        </div>

        <div class="arrow">→</div>

        <div class="workflow-box">
            Best Assignment
        </div>

        <div class="arrow">→</div>

        <div class="workflow-box">
            Change Detected
        </div>

        <div class="arrow">→</div>

        <div class="workflow-box">
            Reallocation
        </div>

    </div>

</div>


<!-- =====================================================
     EMPLOYEE RESOURCES
===================================================== -->

<div class="section">

    <div class="section-header">

        <div>

            <h2>
                1. Workforce Resource State
            </h2>

            <div class="section-description">

                Availability changes immediately influence
                the next AI allocation.

            </div>

        </div>

    </div>


    <div class="table-wrapper">

        <table>

            <tr>

                <th>Name</th>
                <th>Skills</th>
                <th>Workload</th>
                <th>Location</th>
                <th>Performance</th>
                <th>Status</th>
                <th>Action</th>

            </tr>


            {% for employee in employees %}

            <tr>

                <td>
                    <strong>
                        {{ employee.name }}
                    </strong>
                </td>

                <td>
                    {{ employee.skills|join(", ") }}
                </td>

                <td>

                    {{ employee.workload }}%

                    <div class="score-bar">

                        <div
                            class="score-fill"
                            style="width: {{ employee.workload }}%">
                        </div>

                    </div>

                </td>

                <td>
                    {{ employee.location }}
                </td>

                <td>
                    {{ employee.performance }}%
                </td>

                <td>

                    {% if employee.available %}

                    <span class="badge available">
                        AVAILABLE
                    </span>

                    {% else %}

                    <span class="badge unavailable">
                        UNAVAILABLE
                    </span>

                    {% endif %}

                </td>

                <td>

                    <form
                        method="POST"
                        action="/change_status">

                        <input
                            type="hidden"
                            name="name"
                            value="{{ employee.name }}">

                        {% if employee.available %}

                        <button
                            class="danger"
                            type="submit">

                            Make Unavailable

                        </button>

                        {% else %}

                        <button
                            class="success"
                            type="submit">

                            Make Available

                        </button>

                        {% endif %}

                    </form>

                </td>

            </tr>

            {% endfor %}

        </table>

    </div>

</div>


<!-- =====================================================
     TASK INTAKE
===================================================== -->

<div class="section">

    <div class="section-header">

        <div>

            <h2>
                2. Task Intake
            </h2>

            <div class="section-description">

                Every task contains requirements that drive
                the AI allocation decision.

            </div>

        </div>

    </div>


    <div class="table-wrapper">

        <table>

            <tr>

                <th>Task</th>
                <th>Required Skill</th>
                <th>Priority</th>
                <th>SLA</th>
                <th>Location</th>
                <th>Estimated Work</th>

            </tr>


            {% for task in tasks %}

            <tr>

                <td>
                    <strong>
                        {{ task.name }}
                    </strong>
                </td>

                <td>
                    {{ task.skill }}
                </td>

                <td>

                    {% if task.priority == "Critical" %}

                    <span class="badge critical">
                        CRITICAL
                    </span>

                    {% elif task.priority == "High" %}

                    <span class="badge high">
                        HIGH
                    </span>

                    {% elif task.priority == "Medium" %}

                    <span class="badge medium">
                        MEDIUM
                    </span>

                    {% else %}

                    <span class="badge low">
                        LOW
                    </span>

                    {% endif %}

                </td>

                <td>
                    {{ task.sla }} hour(s)
                </td>

                <td>
                    {{ task.location }}
                </td>

                <td>
                    {{ task.estimated_hours }} hour(s)
                </td>

            </tr>

            {% endfor %}

        </table>

    </div>

</div>


<!-- =====================================================
     AI ASSIGNMENTS
===================================================== -->

<div class="section">

    <div class="section-header">

        <div>

            <h2>
                3. AI Allocation Decision
            </h2>

            <div class="section-description">

                Multi-factor scoring selects the most suitable
                available employee for every task.

            </div>

        </div>

    </div>


    <div class="table-wrapper">

        <table>

            <tr>

                <th>Task</th>
                <th>Priority</th>
                <th>Employee</th>
                <th>AI Score</th>
                <th>Decision Factors</th>

            </tr>


            {% for assignment in assignments %}

            <tr>

                <td>
                    <strong>
                        {{ assignment.task }}
                    </strong>
                </td>

                <td>
                    {{ assignment.priority }}
                </td>

                <td>
                    <strong>
                        {{ assignment.employee }}
                    </strong>
                </td>

                <td>

                    <span class="score">
                        {{ assignment.score }}%
                    </span>

                </td>

                <td>

                    {% for reason in assignment.reasons %}

                    <span class="badge stable">
                        {{ reason }}
                    </span>

                    {% endfor %}

                </td>

            </tr>

            {% endfor %}

        </table>

    </div>


    <div class="innovation">

        <h3>
            How the AI decides
        </h3>

        <p>

            <strong>30%</strong> Skill Match &nbsp; • &nbsp;
            <strong>20%</strong> Availability &nbsp; • &nbsp;
            <strong>15%</strong> Workload &nbsp; • &nbsp;
            <strong>15%</strong> Priority &nbsp; • &nbsp;
            <strong>10%</strong> Performance &nbsp; • &nbsp;
            <strong>10%</strong> Location

        </p>

    </div>

</div>


<!-- =====================================================
     INNOVATION 1
===================================================== -->

<div class="section emergency">

    <div class="section-header">

        <div>

            <h2>
                Innovation 1 — Emergency Workforce Swap Chain
            </h2>

            <div class="section-description">

                Instead of assigning a new emergency task independently,
                the system can rearrange existing assignments.

            </div>

        </div>


        {% if emergency_task %}

        <form method="POST" action="/clear_emergency">

            <button
                class="outline"
                type="submit">

                Clear Emergency

            </button>

        </form>

        {% else %}

        <form method="POST" action="/add_emergency">

            <button
                class="danger"
                type="submit">

                Simulate Emergency

            </button>

        </form>

        {% endif %}

    </div>


    {% if emergency_task %}

        {% if emergency_result %}

        <div class="innovation">

            <h3>
                Emergency Detected:
                {{ emergency_task.name }}
            </h3>

            <p>
                Required Skill:
                <strong>{{ emergency_task.skill }}</strong>
                &nbsp; • &nbsp;
                Priority:
                <strong>{{ emergency_task.priority }}</strong>
                &nbsp; • &nbsp;
                SLA:
                <strong>{{ emergency_task.sla }} hour</strong>
            </p>

            <p>
                {{ emergency_result.message }}
            </p>

        </div>


        {% if emergency_result.success %}

        <div class="swap-flow">

            <div class="swap-card">

                <strong>
                    BEFORE
                </strong>

                <br><br>

                Normal allocation

            </div>

            <div class="arrow">
                →
            </div>

            <div class="swap-card">

                <strong>
                    EMERGENCY
                </strong>

                <br><br>

                {{ emergency_result.emergency_employee }}

            </div>

            <div class="arrow">
                →
            </div>

            <div class="swap-card">

                <strong>
                    TASK MOVED
                </strong>

                <br><br>

                {% if emergency_result.replacement %}

                {{ emergency_result.replacement }}

                {% else %}

                Direct assignment

                {% endif %}

            </div>

            <div class="arrow">
                →
            </div>

            <div class="swap-card">

                <strong>
                    FINAL PLAN
                </strong>

                <br><br>

                Emergency protected

            </div>

        </div>


        <div class="table-wrapper">

            <table>

                <tr>

                    <th>Task</th>
                    <th>New Employee</th>
                    <th>Action</th>

                </tr>


                {% for item in emergency_result.after %}

                <tr>

                    <td>
                        {{ item.task }}
                    </td>

                    <td>
                        <strong>
                            {{ item.employee }}
                        </strong>
                    </td>

                    <td>

                        {% if item.reallocated %}

                        <span class="badge high">
                            REALLOCATED
                        </span>

                        {% else %}

                        <span class="badge stable">
                            NO CHANGE
                        </span>

                        {% endif %}

                        <br>

                        {{ item.action }}

                    </td>

                </tr>

                {% endfor %}

            </table>

        </div>

        {% endif %}

        {% endif %}

    {% else %}

        <div class="innovation">

            <h3>
                Live Disruption Simulation
            </h3>

            <p>

                Click <strong>Simulate Emergency</strong> to introduce
                a new critical Networking task.

                The system will determine whether the best employee
                is already busy and, if necessary, move their existing
                task to another suitable employee.

            </p>

        </div>

    {% endif %}

</div>


<!-- =====================================================
     INNOVATION 2 — TASK SPLITTING
===================================================== -->

<div class="section">

    <div class="section-header">

        <div>

            <h2>
                Innovation 2 — Dynamic Task Decomposition
            </h2>

            <div class="section-description">

                A large task can be decomposed into smaller
                skill-specific subtasks and distributed across
                multiple resources.

            </div>

        </div>

    </div>


    <div class="innovation">

        <h3>
            Split a Task
        </h3>

        <p>

            Select a task. The system will break it into
            Planning, Development, Database and Testing
            activities and allocate them independently.

        </p>


        <form
            method="POST"
            action="/split_task">

            <select name="task" required>

                <option value="">
                    Select Task
                </option>

                {% for task in tasks %}

                <option value="{{ task.name }}">

                    {{ task.name }}

                </option>

                {% endfor %}

            </select>

            <button type="submit">

                Split & Allocate

            </button>

        </form>

    </div>


    {% if split_result %}

    <div style="margin-top:20px">

        <h3>

            {{ split_result.original_task }}

            →

            {{ split_result.subtasks|length }}
            Subtasks

        </h3>


        <div class="table-wrapper">

            <table>

                <tr>

                    <th>Subtask</th>
                    <th>Required Skill</th>
                    <th>Assigned Employee</th>
                    <th>AI Score</th>

                </tr>


                {% for item in split_result.allocation %}

                <tr>

                    <td>
                        {{ item.task }}
                    </td>

                    <td>
                        {{ item.skill }}
                    </td>

                    <td>

                        <strong>
                            {{ item.employee }}
                        </strong>

                    </td>

                    <td>

                        <span class="score">
                            {{ item.score }}%
                        </span>

                    </td>

                </tr>

                {% endfor %}

            </table>

        </div>


        <form
            method="POST"
            action="/clear_split"
            style="margin-top:15px">

            <button
                class="outline"
                type="submit">

                Clear Split

            </button>

        </form>

    </div>

    {% endif %}

</div>


<!-- =====================================================
     EARLY WARNING + BACKUP
===================================================== -->

<div class="two-column">


<!-- EARLY WARNING -->

<div class="section">

    <div class="section-header">

        <div>

            <h2>
                4. SLA Early Warning
            </h2>

            <div class="section-description">

                Predicts potential delivery risk from
                workload, urgency, location and SLA pressure.

            </div>

        </div>

    </div>


    {% if warnings %}

        {% for warning in warnings %}

        <div class="
            warning-card
            {% if warning.risk == 'Critical' %}
                critical-card
            {% endif %}
        ">

            <strong>
                {{ warning.task }}
            </strong>

            <br>

            Employee:
            {{ warning.employee }}

            <br>

            Risk:

            {% if warning.risk == "Critical" %}

            <span class="badge critical">
                {{ warning.risk }}
            </span>

            {% elif warning.risk == "High" %}

            <span class="badge high">
                {{ warning.risk }}
            </span>

            {% else %}

            <span class="badge medium">
                {{ warning.risk }}
            </span>

            {% endif %}

            <br>

            Risk Score:
            <strong>
                {{ warning.percentage }}%
            </strong>

            <br><br>

            {{ warning.message }}

        </div>

        {% endfor %}

    {% endif %}

</div>


<!-- SKILL BACKUP -->

<div class="section">

    <div class="section-header">

        <div>

            <h2>
                5. Skill Backup Monitor
            </h2>

            <div class="section-description">

                Detects skills where the organization depends
                on a single employee.

            </div>

        </div>

    </div>


    {% for alert in skill_alerts %}

    <div class="warning-card">

        <strong>
            {{ alert.skill }}
        </strong>

        <br>

        Current Resource:
        {{ alert.employee }}

        <br>

        {% if alert.status == "Single Point of Dependency" %}

        <span class="badge critical">
            SINGLE POINT OF DEPENDENCY
        </span>

        {% else %}

        <span class="badge stable">
            BACKUP AVAILABLE
        </span>

        {% endif %}

        <br><br>

        {{ alert.message }}

    </div>

    {% endfor %}

</div>

</div>


<!-- =====================================================
     SYSTEM HEALTH
===================================================== -->

<div class="section">

    <div class="section-header">

        <div>

            <h2>
                6. Workforce Decision Health
            </h2>

            <div class="section-description">

                Overall operational state calculated from
                availability, workload and task assignment coverage.

            </div>

        </div>

    </div>


    <div class="health">

        <div class="health-circle">

            {{ health }}%

        </div>

        <div>

            <h3 style="margin:0">

                System Status:
                {{ status }}

            </h3>

            <p>

                {{ available }}
                of
                {{ employees|length }}
                employees currently available.

                <br>

                {{ assigned }}
                tasks currently assigned.

                <br>

                {{ critical_warnings }}
                critical SLA warnings.

                <br>

                {{ backup_risks }}
                single-skill dependency alerts.

            </p>

        </div>

    </div>

</div>


<!-- =====================================================
     FINAL DECISION FLOW
===================================================== -->

<div class="section">

    <h2>
        Final AI Decision Architecture
    </h2>

    <div class="workflow">

        <div class="workflow-box">
            Workforce State
        </div>

        <div class="arrow">→</div>

        <div class="workflow-box">
            Task Requirements
        </div>

        <div class="arrow">→</div>

        <div class="workflow-box">
            Multi-Factor Scoring
        </div>

        <div class="arrow">→</div>

        <div class="workflow-box">
            Initial Assignment
        </div>

        <div class="arrow">→</div>

        <div class="workflow-box">
            Live Event
        </div>

        <div class="arrow">→</div>

        <div class="workflow-box">
            Swap / Split
        </div>

        <div class="arrow">→</div>

        <div class="workflow-box">
            SLA Risk
        </div>

        <div class="arrow">→</div>

        <div class="workflow-box">
            Final Decision
        </div>

    </div>

</div>


</div>


<div class="footer">

    AI-04 • AI Workforce Decision & Resource Allocation Agent

    <br>

    Explainable multi-factor workforce optimization prototype

</div>


</body>

</html>

"""


# ============================================================
# 22. RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )