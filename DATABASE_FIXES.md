# Database Relationship Fixes

## Issues Fixed

### 1. KYC Document Ambiguity ✅
**Problem:** `KYCDocument` has two foreign keys to `User` table:
- `user_id` (the developer submitting KYC)
- `reviewed_by` (the admin reviewing)

**Solution:** Added `foreign_keys='KYCDocument.user_id'` to `User.kyc_documents` relationship in `app/models/user.py`

```python
# Before
kyc_documents = db.relationship('KYCDocument', backref='user', lazy=True)

# After
kyc_documents = db.relationship('KYCDocument', foreign_keys='KYCDocument.user_id', backref='user', lazy=True)
```

### 2. Project-Team Circular Relationship ✅
**Problem:** Circular foreign key relationship:
- `Team.project_id` → `Project.id`
- `Project.assigned_team_id` → `Team.id`

**Solution:** Added `foreign_keys='Team.project_id'` to `Project.team` relationship in `app/models/project.py`

```python
# Before
team = db.relationship('Team', backref='project', uselist=False)

# After
team = db.relationship('Team', foreign_keys='Team.project_id', backref='project', uselist=False)
```

## All Fixed Relationships

### User Model (`app/models/user.py`)
```python
kyc_documents = db.relationship('KYCDocument', foreign_keys='KYCDocument.user_id', backref='user', lazy=True)
```

### Project Model (`app/models/project.py`)
```python
team = db.relationship('Team', foreign_keys='Team.project_id', backref='project', uselist=False)
reviewer = db.relationship('User', foreign_keys=[reviewed_by])
```

### Team Model (`app/models/team.py`)
```python
lead = db.relationship('DeveloperProfile', foreign_keys=[lead_developer_id])
creator = db.relationship('User', foreign_keys=[created_by])
```

### KYC Model (`app/models/kyc.py`)
```python
reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='kyc_reviews')
```

### Appointment Model (`app/models/appointment.py`)
```python
canceller = db.relationship('User', foreign_keys=[cancelled_by])
```

## Status
✅ All ambiguous foreign key relationships have been resolved.
✅ The application should now run without SQLAlchemy errors.

## Testing
After these fixes, the Flask development server should automatically reload and the application should work at `http://localhost:5000`
