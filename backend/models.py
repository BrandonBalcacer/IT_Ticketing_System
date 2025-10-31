from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy (this connects your Python code to the database)
db = SQLAlchemy()

class User(db.Model):
    """
    User model - stores information about all users in the system
    This includes regular employees, IT technicians, and managers
    """
    __tablename__ = 'users'
    
    # Primary key - unique identifier for each user
    id = db.Column(db.Integer, primary_key=True)
    
    # User credentials and info
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Role determines what the user can do (user, technician, manager)
    role = db.Column(db.String(20), nullable=False, default='user')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship - connects users to their tickets
    tickets = db.relationship('Ticket', backref='creator', lazy=True, foreign_keys='Ticket.created_by')
    assigned_tickets = db.relationship('Ticket', backref='assigned_technician', lazy=True, foreign_keys='Ticket.assigned_to')
    
    def set_password(self, password):
        """Hash the password before storing (security best practice)"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify a password against the stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary for JSON responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }


class Ticket(db.Model):
    """
    Ticket model - stores all support tickets submitted by users
    """
    __tablename__ = 'tickets'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Ticket details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Hardware, Software, Network, etc.
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), nullable=False, default='open')  # open, in_progress, resolved, closed
    
    # Foreign keys - connect tickets to users
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship to activity logs
    activities = db.relationship('ActivityLog', backref='ticket', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert ticket object to dictionary for JSON responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class ActivityLog(db.Model):
    """
    Activity Log model - tracks all changes made to tickets
    This creates an audit trail showing who did what and when
    """
    __tablename__ = 'activity_logs'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key - which ticket this activity belongs to
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    
    # Foreign key - who performed this action
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Activity details
    action = db.Column(db.String(100), nullable=False)  # "created", "assigned", "status_changed", etc.
    description = db.Column(db.Text, nullable=False)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = db.relationship('User', backref='activities')
    
    def to_dict(self):
        """Convert activity log to dictionary for JSON responses"""
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'user_id': self.user_id,
            'action': self.action,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }