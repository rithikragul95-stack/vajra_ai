# VAJRA AI: Supply Chain Intelligence Engine

## Overview 
VAJRA AI is a comprehensive, advanced Supply Chain Risk Management platform designed to dynamically assess, predict, and mitigate disruptions. The system ingests vast amounts of operational pipeline data (e.g., inventory levels, demand, lead times) alongside external geographical and geopolitical risk factors (e.g., flood zones, earthquake probabilities, transport disruptions).

We use a proprietary **5-Phase Intelligence Pipeline** to compute risk matrices and recommend actionable, prescriptive interventions before disruptions hit the bottom line.

---

## 🏗️ Architecture & Technology Stack

The platform is designed intelligently as a monolithic micro-kernel API connected to a lightweight frontend display, allowing for rapid deployment, extreme scalability, and AI-driven intelligence computing.

### 1. Backend API (The Brain)
- **FastAPI (Python):** The core routing backend. Chosen for its extreme performance (built on Starlette) and native asynchronous capabilities. It allows us to process thousands of supplier metrics in parallel and handles the complex 5-phase algorithmic computations with minimal latency. It inherently self-documents and validates all payload data using **Pydantic**.
- **Python (scikit-learn, joblib, pandas):** The underlying engine executing the intelligence algorithms. 
  - *Pandas* is used for robust, large-scale data ingestion and data-frame manipulations from CSV and external integrations (such as the Northwind pipeline).
  - *scikit-learn* (and placeholders for future XGBoost integrations) are utilized in our Phase 3 Predictive Engine to weigh feature severities.
- **SQLAlchemy & SQLite:** Safe, resilient data storage. We use an ORM (Object-Relational Mapping, via SQLAlchemy) to easily manage database migrations and ensure security against SQL injections, maintaining persistent records of every algorithmic snapshot generated for suppliers over time.

### 2. Frontend Interface (The Dashboard)
- **Vanilla JavaScript, HTML5, & CSS3:** The entire frontend is constructed without heavyweight frameworks (like React or Angular) to ensure an ultra-fast, zero-dependency footprint.
- **Chart.js:** We integrated this specific library because of its smooth HTML5 Canvas rendering. Chart.js generates our dynamic Risk Radar Graphs and Inventory Bar gaps, visualizing complex composite scores so executives can understand them in seconds.
- **FontAwesome:** Used for standardized iconography throughout the application to elevate the UI's modern SaaS aesthetic.

---

## 🧠 The 5-Phase Intelligence Pipeline

Our competitive advantage lies in the integration API, housed in the `engine/` directory, which executes 5 distinct mathematical phases for every analyzed supplier:

### Phase 1: Data Ingestion & Unification
The system maps disparate operational data points (Demand, Inventory, Lead Time) and Risk data (Floods, Infrastructure delays, Political Instability) into a unified `SystemInput` matrix.

### Phase 2: Inventory Exposure & Dynamic Lead Time Safety
*Calculates true physical vulnerability.* It projects how long current inventory will last (Inventory Cover) against the total incoming lead time minus expected delays. If the gap is negative, it triggers immediate exposure flags.

### Phase 3: Predictive External Risk Scoring
*Applies Machine Learning weights.* Combines all geopolitical, natural, and transportation risks into a single **Supplier Risk Probability (SRP)** ranging from 0.0 to 1.0, categorizing risks into High, Medium, or Low tiers.

### Phase 4: Threat Integration & Composite Vulnerability Index (CVI)
*The Core Metric.* This phase marries the internal Phase 2 weakness (lack of stock) with external Phase 3 threats (high environmental risk) to compute the **CVI Score**. This score actively sorts suppliers into actionable tiers—from "Preventive Monitoring" up to "Critical Alert".

### Phase 5: Prescriptive Action Generation
*Automated decision-making.* Based on the CVI threshold and localized bottlenecks, the AI generates specific JSON-formatted directives for Procurement teams. For example, it exactly calculates the *Additional Inventory Needed* to offset calculated risk delays and output commands like *"Expedite air freight routing to bypass infrastructure threats."* 

---

## 🚀 Business Value for Investors 
By marrying localized ERP metrics with global risk data, VAJRA AI stops supply chain disruptions proactively. It replaces a dozen siloed Excel sheets into one unified, visual, and highly prescriptive dashboard—offering immediate ROI through prevented stockouts and optimized disaster routing.
