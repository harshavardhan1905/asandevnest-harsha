# Asan DevNest - Implementation Plan

## 🎯 Project Overview
**Asan DevNest** is a production-level web platform that connects verified developers with clients in a secure, legally responsible, team-based execution model.

### Core Differentiators
- **NOT a freelance marketplace** - Asan takes full responsibility
- **Trust-based discovery** - Developers discovered through content, not profiles
- **Team-based execution** - Admin forms teams, manages delivery
- **Legal safety** - KYC verification, compliance management

---

## 📁 Project Structure

```
asan_devnest/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration settings
│   ├── extensions.py            # Flask extensions
│   │
│   ├── models/                  # SQLAlchemy Models
│   │   ├── __init__.py
│   │   ├── user.py              # User, Admin, Developer, Client
│   │   ├── article.py           # Articles & content
│   │   ├── project.py           # Projects & ideas
│   │   ├── appointment.py       # Booking system
│   │   ├── team.py              # Team management
│   │   └── kyc.py               # KYC documents
│   │
│   ├── routes/                  # Flask Blueprints (Controllers)
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication routes
│   │   ├── admin.py             # Admin dashboard routes
│   │   ├── developer.py         # Developer routes
│   │   ├── client.py            # Client routes
│   │   ├── articles.py          # Community articles routes
│   │   └── api.py               # API endpoints
│   │
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── kyc_service.py
│   │   ├── article_service.py
│   │   ├── project_service.py
│   │   ├── team_service.py
│   │   └── appointment_service.py
│   │
│   ├── templates/               # Jinja2 Templates
│   │   ├── base.html
│   │   ├── components/          # Reusable components
│   │   ├── auth/                # Login, Register
│   │   ├── admin/               # Admin dashboard
│   │   ├── developer/           # Developer dashboard
│   │   ├── client/              # Client dashboard
│   │   ├── articles/            # Community page
│   │   └── public/              # Public pages
│   │
│   ├── static/                  # Static assets
│   │   ├── css/
│   │   │   └── styles.css       # Custom styles
│   │   ├── js/
│   │   │   └── main.js          # JavaScript
│   │   └── images/
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── decorators.py        # Role-based access
│       ├── validators.py        # Form validation
│       └── helpers.py           # Helper functions
│
├── uploads/                     # File storage
│   ├── kyc/                     # KYC documents
│   ├── articles/                # Article images
│   ├── portfolios/              # Portfolio files
│   └── projects/                # Project files
│
├── migrations/                  # Database migrations
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # Documentation
```

---

## 🗃️ Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| email | String | Unique email |
| password_hash | String | Hashed password |
| role | Enum | admin/developer/client |
| full_name | String | Full name |
| phone | String | Phone number |
| avatar | String | Profile image path |
| status | Enum | pending/verified/rejected |
| created_at | DateTime | Registration date |
| updated_at | DateTime | Last update |

### Developer Profile
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| user_id | Integer | FK to Users |
| bio | Text | Developer bio |
| skills | JSON | Skills array |
| domains | JSON | Expertise domains |
| experience_years | Integer | Years of experience |
| hourly_rate | Decimal | Consulting rate |
| portfolio_url | String | External portfolio |
| linkedin_url | String | LinkedIn profile |
| github_url | String | GitHub profile |
| availability | Enum | available/busy/unavailable |

### KYC Documents
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| user_id | Integer | FK to Users |
| document_type | String | ID type |
| document_path | String | File path |
| status | Enum | pending/approved/rejected |
| admin_notes | Text | Admin remarks |
| submitted_at | DateTime | Submission date |
| reviewed_at | DateTime | Review date |

### Articles
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| developer_id | Integer | FK to Developer |
| title | String | Article title |
| slug | String | URL slug |
| content | Text | Article content |
| excerpt | Text | Short summary |
| cover_image | String | Cover image path |
| article_type | Enum | case_study/research/tutorial |
| technologies | JSON | Tech tags |
| domain | String | Industry domain |
| status | Enum | draft/pending/approved/rejected |
| views_count | Integer | View count |
| published_at | DateTime | Publish date |

### Appointments
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| client_id | Integer | FK to Client |
| developer_id | Integer | FK to Developer |
| appointment_type | Enum | class/consulting/support |
| scheduled_at | DateTime | Appointment time |
| duration_minutes | Integer | Duration |
| status | Enum | pending/confirmed/completed/cancelled |
| notes | Text | Client notes |
| meeting_link | String | Video call link |

### Projects (Client Ideas)
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| client_id | Integer | FK to Client |
| title | String | Project title |
| description | Text | Full description |
| budget_range | String | Budget range |
| timeline | String | Expected timeline |
| technologies | JSON | Required tech |
| domain | String | Industry domain |
| status | Enum | submitted/reviewing/assigned/in_progress/completed |
| assigned_team_id | Integer | FK to Teams |

### Teams
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| name | String | Team name |
| project_id | Integer | FK to Projects |
| lead_developer_id | Integer | Team lead |
| status | Enum | forming/active/completed |
| deadline | DateTime | Delivery deadline |
| created_at | DateTime | Formation date |

### Team Members (Junction)
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| team_id | Integer | FK to Teams |
| developer_id | Integer | FK to Developer |
| role | String | Member role |
| joined_at | DateTime | Join date |

---

## 🎨 UI/UX Design System

### Color Palette
- **Primary**: #6366F1 (Indigo)
- **Secondary**: #8B5CF6 (Violet)
- **Accent**: #06B6D4 (Cyan)
- **Success**: #10B981 (Emerald)
- **Warning**: #F59E0B (Amber)
- **Error**: #EF4444 (Red)
- **Dark**: #0F172A (Slate 900)
- **Light**: #F8FAFC (Slate 50)

### Typography
- **Headings**: Inter (Google Fonts)
- **Body**: Inter
- **Code**: JetBrains Mono

### Components
- Glassmorphism cards
- Gradient buttons
- Animated badges
- Smooth transitions
- Modern form inputs
- Premium dashboards

---

## 🔐 Security Features

1. **Authentication**
   - Secure password hashing (Werkzeug)
   - Session-based auth with Flask-Login
   - CSRF protection

2. **Authorization**
   - Role-based access control decorators
   - Route protection by role

3. **KYC Verification**
   - Document upload & storage
   - Admin review workflow
   - Status tracking

4. **Data Validation**
   - Input sanitization
   - File type validation
   - Size limits

---

## 📋 Implementation Phases

### Phase 1: Foundation (Core Setup)
- [x] Project structure
- [ ] Flask app factory
- [ ] Database models
- [ ] Authentication system
- [ ] Base templates

### Phase 2: Admin Module
- [ ] Admin dashboard
- [ ] Developer verification
- [ ] Article moderation
- [ ] Project management
- [ ] Team creation

### Phase 3: Developer Module
- [ ] Registration flow
- [ ] KYC submission
- [ ] Profile management
- [ ] Article creation
- [ ] Appointment setup

### Phase 4: Client Module
- [ ] Client dashboard
- [ ] Developer discovery
- [ ] Article browsing
- [ ] Idea submission
- [ ] Appointment booking

### Phase 5: Community Features
- [ ] Articles page
- [ ] Search & filters
- [ ] Developer profiles
- [ ] "Build with Asan" CTAs

### Phase 6: Polish & Launch
- [ ] UI refinement
- [ ] Error handling
- [ ] Testing
- [ ] Documentation

---

## 🚀 Getting Started

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db init
flask db migrate
flask db upgrade

# Create admin user
flask create-admin

# Run application
flask run
```

---

## 📝 Notes

- All file uploads stored locally with paths in DB
- Ready for PostgreSQL migration
- Scalable blueprint-based architecture
- Production-ready folder structure
