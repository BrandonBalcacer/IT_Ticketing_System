# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 13:03:23 2025

@author: user
"""
# IT Help Desk Ticketing System

Full-stack web application for managing IT support tickets with role-based access control.

## Features
- User authentication with password hashing
- Role-based permissions (User, Technician, Manager)
- Ticket creation, assignment, and tracking
- Complete audit trail of all actions (WIP) 
- Responsive web interface
 - Admin statistics and reporting (WIP)
   
## Tech Stack
- **Backend:** Python, Flask, SQLAlchemy
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** PostgreSQL (production), SQLite (development)
- **Deployment:** AWS EC2, RDS, S3 (in progress)

## Local Setup
```bash
# Clone repository
git clone https://github.com/BrandonBalcacer/IT_Ticketing_System.git

# Create virtual environment
conda create -n helpdesk-flask python=3.9
conda activate helpdesk-flask

# Install dependencies
pip install -r requirements.txt

# Run application
python -m backend.app
```

## Demo
Backend API: `http://127.0.0.1:5000`
Frontend: Open `frontend/login.html` in browser
 
## Project Timeline
   
- Phase 1: Environment Setup (Done)
- Phase 2: Backend Development(Done)
- Phase 3: Frontend Development(Modyifying)
- Phase 4: AWS Deployment (Current)
- Phase 5: Testing and Documentation


## Author
Brandon Balcacer
# IT Help Desk Ticketing System
 
