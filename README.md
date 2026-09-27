# AI-Assisted Academic Timetable & Study Planner

## Pace AI Study Planner Project - Year 3, Semester 2, 2026

---

## 📋 Project Structure

```
timetable_planner_project/
├── backend/                    # Django REST API
│   ├── apps/
│   │   ├── accounts/          # User authentication & profiles
│   │   ├── timetable/         # Courses, schedules, assignments
│   │   ├── scheduler/         # AI study plan generation (OR-Tools)
│   │   ├── attendance/        # Attendance tracking & alerts
│   │   └── study_groups/      # Group study matching
│   ├── config/                # Django settings
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment variables template
│   └── manage.py              # Django management script
├── frontend/                   # React.js application
│   ├── public/                # Static files
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API services
│   │   ├── utils/              # Utilities (AuthContext, API)
│   │   └── styles/             # CSS stylesheets
│   └── package.json            # Node dependencies
└── docs/                       # Documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (optional; SQLite is the default for local development)
- Redis 7+ (optional; only needed for Celery background tasks)

---

## Step 1: Backend Setup

### 1.1 Create Virtual Environment
```powershell
cd backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### 1.2 Install Dependencies
```bash
pip install -r requirements.txt
```

### 1.3 Configure Environment Variables
```powershell
Copy-Item .env.example .env
# SQLite is the default; no database server is required for local development.
```

### 1.4 Optional PostgreSQL Database
```sql
CREATE DATABASE timetable_db;
CREATE USER postgres WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE timetable_db TO postgres;
```

### 1.5 Run Migrations
```bash
python manage.py makemigrations accounts timetable scheduler attendance study_groups
python manage.py migrate
```

### 1.6 Create Superuser
```bash
python manage.py createsuperuser
```

### 1.7 Start Development Server
```bash
python manage.py runserver
```

If PowerShell blocks virtual-environment activation, run this once for your user account:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Backend will be available at: http://localhost:8000

---

## Step 2: Frontend Setup

### 2.1 Install Dependencies
```bash
cd frontend
npm install
```

### 2.2 Start Development Server
```bash
npm start
```

Frontend will be available at: http://localhost:3000

---

## Step 3: Redis & Celery (Optional - for background tasks)

### 3.1 Start Redis Server
```bash
redis-server
```

### 3.2 Start Celery Worker
```bash
cd backend
celery -A config worker -l info
```

---

## 🔑 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register/ | Register new student |
| POST | /api/auth/login/ | Login |
| POST | /api/auth/logout/ | Logout |
| GET | /api/auth/profile/ | Get profile |
| PATCH | /api/auth/profile/ | Update profile |

### Timetable
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/timetable/courses/ | List courses |
| GET | /api/timetable/schedules/ | List class schedules |
| GET | /api/timetable/my-courses/ | My enrolled courses |
| POST | /api/timetable/enroll/ | Enroll in course |
| GET | /api/timetable/assignments/ | List assignments |
| GET | /api/timetable/conflicts/ | Detect conflicts |
| GET | /api/timetable/dashboard/ | Dashboard summary |

### AI Study Planner
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/scheduler/generate/ | Generate AI study plan |
| GET | /api/scheduler/plans/ | List study plans |
| POST | /api/scheduler/sessions/{id}/complete/ | Mark session complete |

### Attendance
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/attendance/mark/ | Mark attendance |
| GET | /api/attendance/summaries/ | Attendance summaries |
| GET | /api/attendance/alerts/ | Attendance alerts |

### Study Groups
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/study-groups/groups/ | List groups |
| GET | /api/study-groups/find/ | AI-recommended groups |
| POST | /api/study-groups/groups/{id}/join/ | Join group |

---

## 🤖 AI Algorithm Details

### Study Plan Generation (OR-Tools CP-SAT)

The system uses Google OR-Tools constraint programming solver to:

1. **Define Variables**: Binary indicators for each potential study slot
2. **Hard Constraints**:
   - No overlap with existing classes
   - Maximum hours per day limit
   - Minimum study time per course (based on credits)

3. **Objective Function**: Maximize study quality score
   - `Score = difficulty × preference_alignment × deadline_proximity`

4. **Output**: Optimized study sessions grouped by day and time

### Conflict Detection
- **Interval Tree Search**: O(n log n) complexity
- Detects overlapping classes, back-to-back exams, deadline clustering

### Group Study Matching
- **Compatibility Score**: Based on shared courses, free time overlap, group size
- **Bipartite Matching**: Hungarian algorithm variant for optimal group formation

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 📦 Deployment

### Production Build
```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
python manage.py collectstatic
python manage.py migrate
```

### Using Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

---

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_NAME | PostgreSQL database name | timetable_db |
| DATABASE_USER | Database user | postgres |
| DATABASE_PASSWORD | Database password | - |
| SECRET_KEY | Django secret key | dev-key |
| DEBUG | Debug mode | True |
| REDIS_URL | Redis connection URL | redis://localhost:6379/0 |

---

## 👥 Team Members

- [Group Leader Name]
- [Member 2]
- [Member 3]
- [Member 4]

**Supervisor**: [Supervisor Name]

---

## 📚 References

1. Schwalbe, K. (2019). *Information Technology Project Management* (9th ed.)
2. Google OR-Tools Documentation: https://developers.google.com/optimization
3. Django REST Framework: https://www.django-rest-framework.org
4. React Documentation: https://react.dev

---

**Project Status**: In Development
**Last Updated**: May 2026


## Pace Admin Dashboard

Create an administrator account from the backend directory:

```powershell
python manage.py createsuperuser
```

Start both servers, sign in at `http://localhost:3000`, and open:

```text
http://localhost:3000/admin-dashboard
```

Only Django staff users can access this dashboard. It provides statistics and management sections for users, courses, class schedules, assignments, exams, study groups, and attendance records. The dashboard also links to Django Admin at `http://127.0.0.1:8000/admin/` for advanced model-level editing.
