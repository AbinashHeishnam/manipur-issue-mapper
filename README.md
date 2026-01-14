# 🛣️ Manipur Issue Mapper
### AI-Powered Civic Issue Reporting & Red Zone Mapping System

**Manipur Issue Mapper** is a next-generation civic technology platform designed to empower citizens and government authorities. It aggregates citizen reports on infrastructure and utility issues (like potholes, water leaks, uncollected garbage), applies **AI analysis** for classification and fraud detection, and visualizes data on a **Live Heatmap**.

---

## 🚀 Key Features

### 🧠 Artificial Intelligence
- **Smart Classification**: Automatically categorizes issues (e.g., *Road, Water, Electricity*) and estimates **Severity (1-5)**.
- **Spam & Fraud Detection**: Filters out fake reports (e.g., "Free iPhone", "Earn Money") before they reach the system.
- **Auto-Priority**: Issues are prioritized based on keyword analysis and severity scores.

### 👥 Role-Based Portals
- **Citizen Portal**:
  - Report issues with location (GPS) and description.
  - Track status of reported issues via a personalized dashboard.
  - View "Live Heatmap" of issues across the region.
- **Admin Dashboard**:
  - Review all incoming issues with AI insights.
  - Approve or Reject issues (with Spam warnings).
  - Assign issues to specific departments (e.g., *Sanitation, Police, PWD*).
- **Department Portal**:
  - View assigned tasks/issues.
  - Update status (e.g., *In Progress, Resolved*).
  - Add completion notes.

### 🎨 Modern Experience
- **Glassmorphism UI**: Beautiful, translucent interface for a modern feel.
- **Live Maps**: Interactive Leaflet maps for reporting and visualization.
- **Real-time Feedback**: Animated toast notifications for all actions.

---

## �️ Technology Stack

- **Frontend**: 
  - Standard HTML5, CSS3 (Custom Glassmorphism), JavaScript (ES6+)
  - **Leaflet.js** (Interactive Maps & Heatmaps)
- **Backend**: 
  - **Python** (FastAPI)
  - **Uvicorn** (ASGI Server)
- **Database**: 
  - **MySQL** (Relational Data & Geospatial storage)
- **AI & Machine Learning**: 
  - **Scikit-Learn**: TF-IDF Vectorization, Logistic Regression.
  - **Pandas**: Data processing.
  - **Joblib**: Model serialization.
  - **Nominatim API**: Reverse Geocoding.

---

## � Project Structure

```
manipur-issue-mapper/
├── ai/                     # AI Models & Training Scripts
│   ├── artifacts/          # Saved Models (.pkl)
│   ├── data/               # Training Datasets (.csv)
│   ├── model.py            # Classification Logic
│   └── fraud.py            # Fraud Detection Logic
├── backend/                # FastAPI Backend
│   ├── main.py             # App Entry Point
│   └── routes/             # API Endpoints (Issues, Admin, Dept)
├── frontend/               # User Interface
│   ├── index.html          # Reporting Portal
│   ├── live.html           # Heatmap
│   ├── admin/              # Admin Dashboard
│   └── department/         # Department Dashboard
└── database/               # SQL Scripts
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/AbinashHeishnam/manipur-issue-mapper.git
cd manipur-issue-mapper
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database
1. Make sure **MySQL** is running.
2. Create a database named `issue_mapper`.
3. Import the schema:
   ```bash
   mysql -u root -p issue_mapper < database/init_db.sql
   ```
4. Update `backend/utils/db_utils.py` with your MySQL credentials.

### 5. Train AI Models
Run the training scripts to generate the `.pkl` artifacts:
```bash
# Train Fraud Detector
python -m ai.train_fraud

# Train Category/Severity Classifier
python -m ai.train
```

### 6. Run the Application
```bash
uvicorn backend.main:app --reload
```
Access the app at: `http://127.0.0.1:8000/frontend/index.html`

---

## 🛡️ License
This project is developed for the **Manipur Civic Tech Hackathon**.

> **"Let data decide priority, not manual complaints."**
