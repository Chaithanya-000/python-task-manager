"""
Database Models Module
Defines the SQLAlchemy database instance and Task model.
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_utc_now():
    """Helper returning timezone-aware current UTC time."""
    return datetime.now(timezone.utc)


class Task(db.Model):
    """
    Task database model representing a work item in the Task Manager.
    
    Fields:
      - id: Unique primary key integer
      - title: Short title of the task (required, max 150 chars)
      - description: Detailed notes or instructions (optional)
      - priority: 'Low', 'Medium', or 'High' (defaults to 'Medium')
      - status: 'Pending' or 'Completed' (defaults to 'Pending')
      - created_at: Timestamp when created (UTC)
      - updated_at: Timestamp when last updated (UTC)
    """
    __tablename__ = 'tasks'

    VALID_PRIORITIES = ['Low', 'Medium', 'High']
    VALID_STATUSES = ['Pending', 'Completed']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), nullable=False, default='Medium')
    status = db.Column(db.String(20), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, nullable=False, default=get_utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=get_utc_now, onupdate=get_utc_now)

    def __init__(self, title, description=None, priority='Medium', status='Pending'):
        self.title = title.strip() if title else ''
        self.description = description.strip() if description else ''
        self.priority = priority.capitalize() if priority else 'Medium'
        self.status = status.capitalize() if status else 'Pending'

    def to_dict(self):
        """Serialize Task model instance to a JSON-compatible dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description or '',
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'created_at_iso': self.created_at.isoformat() if self.created_at else None,
            'updated_at_iso': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Task id={self.id} title='{self.title[:20]}' status='{self.status}'>"
