"""
Python Task Manager - Flask Application
Production-ready REST API and modern SaaS Dashboard.
"""

import os
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from sqlalchemy import or_, text
from models import db, Task
from config import config_by_name


def create_app(config_name=None):
    """
    Application factory pattern to configure and create the Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development').lower()

    app = Flask(__name__)
    config_obj = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_obj)

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Initialize database tables automatically within app context
    with app.app_context():
        db.create_all()

    # ---------------------------------------------------------
    # CLI Commands for CI/CD and deployment tasks
    # ---------------------------------------------------------
    @app.cli.command("init-db")
    def init_db():
        """Initialize and create database tables."""
        db.create_all()
        print("Database initialized successfully.")

    @app.cli.command("seed-db")
    def seed_db():
        """Seed database with sample tasks for demonstration."""
        samples = [
            ("Set up GitHub Actions CI/CD Pipeline", "Configure workflows for testing and linting", "High", "Completed"),
            ("Containerize App with Docker", "Write multi-stage Dockerfile and test image builds", "High", "Pending"),
            ("Deploy to AWS EC2 with Nginx", "Configure reverse proxy and systemd service on EC2", "Medium", "Pending"),
            ("Write Automated Pytest Test Suite", "Achieve high coverage on all REST API endpoints", "Medium", "Completed"),
            ("Implement UI dark/light theme", "Refine SaaS dashboard components and responsiveness", "Low", "Pending"),
        ]
        for title, desc, priority, status in samples:
            existing = Task.query.filter_by(title=title).first()
            if not existing:
                task = Task(title=title, description=desc, priority=priority, status=status)
                db.session.add(task)
        db.session.commit()
        print("Database seeded with sample tasks.")

    # ---------------------------------------------------------
    # Health Check Endpoint (DevOps / Docker / Load Balancer)
    # ---------------------------------------------------------
    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint for Docker HEALTHCHECK, AWS ALB/ELB, and Jenkins verification.
        Returns HTTP 200 if the application and database connection are healthy.
        """
        try:
            # Verify database connectivity
            db.session.execute(text('SELECT 1'))
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'version': '1.0.0'
            }), 200
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 503

    # ---------------------------------------------------------
    # Web UI Dashboard Routes
    # ---------------------------------------------------------
    @app.route('/', methods=['GET'])
    def dashboard():
        """Render the primary SaaS dashboard."""
        return render_template('index.html')

    # ---------------------------------------------------------
    # REST API Endpoints
    # ---------------------------------------------------------
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """
        Return summary statistics:
        - total tasks
        - completed tasks
        - pending tasks
        - task completion percentage
        - priority breakdown
        """
        total = Task.query.count()
        completed = Task.query.filter_by(status='Completed').count()
        pending = Task.query.filter_by(status='Pending').count()
        completion_percentage = round((completed / total * 100), 1) if total > 0 else 0.0

        high_priority = Task.query.filter_by(priority='High').count()
        medium_priority = Task.query.filter_by(priority='Medium').count()
        low_priority = Task.query.filter_by(priority='Low').count()

        return jsonify({
            'total': total,
            'completed': completed,
            'pending': pending,
            'completion_percentage': completion_percentage,
            'priority_breakdown': {
                'high': high_priority,
                'medium': medium_priority,
                'low': low_priority
            }
        }), 200

    @app.route('/api/tasks', methods=['GET'])
    def get_tasks():
        """
        Retrieve all tasks with optional search query and filters.
        Query params:
          - search: search keyword matching title or description
          - status: 'All', 'Pending', 'Completed'
          - priority: 'All', 'Low', 'Medium', 'High'
          - sort_by: 'created_at', 'updated_at', 'priority', 'title'
          - order: 'asc', 'desc'
        """
        query = Task.query

        # Filter by search string
        search = request.args.get('search', '').strip()
        if search:
            query = query.filter(
                or_(
                    Task.title.ilike(f'%{search}%'),
                    Task.description.ilike(f'%{search}%')
                )
            )

        # Filter by status
        status = request.args.get('status', '').strip().capitalize()
        if status in Task.VALID_STATUSES:
            query = query.filter_by(status=status)

        # Filter by priority
        priority = request.args.get('priority', '').strip().capitalize()
        if priority in Task.VALID_PRIORITIES:
            query = query.filter_by(priority=priority)

        # Sorting
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc').lower()

        sort_column = getattr(Task, sort_by, Task.created_at)
        if order == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        tasks = query.all()
        return jsonify({
            'count': len(tasks),
            'tasks': [t.to_dict() for t in tasks]
        }), 200

    @app.route('/api/tasks', methods=['POST'])
    def create_task():
        """
        Create a new task.
        Accepts JSON payload: { title, description?, priority?, status? }
        """
        data = request.get_json(silent=True) or request.form.to_dict()

        if not data:
            return jsonify({'error': 'Request payload must be valid JSON or form data.'}), 400

        title = data.get('title', '').strip()
        if not title:
            return jsonify({'error': 'Task title is required and cannot be empty.'}), 400

        if len(title) > 150:
            return jsonify({'error': 'Task title cannot exceed 150 characters.'}), 400

        description = data.get('description', '').strip()
        priority = data.get('priority', 'Medium').capitalize()
        if priority not in Task.VALID_PRIORITIES:
            return jsonify({
                'error': f"Invalid priority '{priority}'. Allowed: {', '.join(Task.VALID_PRIORITIES)}"
            }), 400

        status = data.get('status', 'Pending').capitalize()
        if status not in Task.VALID_STATUSES:
            return jsonify({
                'error': f"Invalid status '{status}'. Allowed: {', '.join(Task.VALID_STATUSES)}"
            }), 400

        task = Task(title=title, description=description, priority=priority, status=status)
        db.session.add(task)
        db.session.commit()

        return jsonify({
            'message': 'Task created successfully.',
            'task': task.to_dict()
        }), 201

    @app.route('/api/tasks/<int:task_id>', methods=['GET'])
    def get_task(task_id):
        """Retrieve a specific task by its unique ID."""
        task = db.session.get(Task, task_id)
        if not task:
            return jsonify({'error': f"Task with ID {task_id} not found."}), 404
        return jsonify(task.to_dict()), 200

    @app.route('/api/tasks/<int:task_id>', methods=['PUT', 'PATCH'])
    def update_task(task_id):
        """
        Update an existing task (full or partial update).
        Accepts: { title?, description?, priority?, status? }
        """
        task = db.session.get(Task, task_id)
        if not task:
            return jsonify({'error': f"Task with ID {task_id} not found."}), 404

        data = request.get_json(silent=True) or request.form.to_dict()
        if not data:
            return jsonify({'error': 'Request payload must not be empty.'}), 400

        if 'title' in data:
            new_title = data['title'].strip()
            if not new_title:
                return jsonify({'error': 'Task title cannot be empty.'}), 400
            if len(new_title) > 150:
                return jsonify({'error': 'Task title cannot exceed 150 characters.'}), 400
            task.title = new_title

        if 'description' in data:
            task.description = data['description'].strip()

        if 'priority' in data:
            new_priority = data['priority'].capitalize()
            if new_priority not in Task.VALID_PRIORITIES:
                return jsonify({
                    'error': f"Invalid priority '{new_priority}'. Allowed: {', '.join(Task.VALID_PRIORITIES)}"
                }), 400
            task.priority = new_priority

        if 'status' in data:
            new_status = data['status'].capitalize()
            if new_status not in Task.VALID_STATUSES:
                return jsonify({
                    'error': f"Invalid status '{new_status}'. Allowed: {', '.join(Task.VALID_STATUSES)}"
                }), 400
            task.status = new_status

        task.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        return jsonify({
            'message': 'Task updated successfully.',
            'task': task.to_dict()
        }), 200

    @app.route('/api/tasks/<int:task_id>/status', methods=['PATCH', 'POST'])
    def toggle_task_status(task_id):
        """
        Quick endpoint to toggle or explicitly set a task's status.
        Optional body: { "status": "Completed" | "Pending" }
        If body is omitted, toggles between Completed and Pending.
        """
        task = db.session.get(Task, task_id)
        if not task:
            return jsonify({'error': f"Task with ID {task_id} not found."}), 404

        data = request.get_json(silent=True) or {}
        new_status = data.get('status')

        if new_status:
            normalized_status = new_status.capitalize()
            if normalized_status not in Task.VALID_STATUSES:
                return jsonify({
                    'error': f"Invalid status '{new_status}'. Allowed: {', '.join(Task.VALID_STATUSES)}"
                }), 400
            task.status = normalized_status
        else:
            # Toggle between Pending and Completed
            task.status = 'Completed' if task.status == 'Pending' else 'Pending'

        task.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        return jsonify({
            'message': f"Task marked as {task.status}.",
            'task': task.to_dict()
        }), 200

    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        """Delete a task by ID."""
        task = db.session.get(Task, task_id)
        if not task:
            return jsonify({'error': f"Task with ID {task_id} not found."}), 404

        db.session.delete(task)
        db.session.commit()

        return jsonify({
            'message': 'Task deleted successfully.',
            'id': task_id
        }), 200

    # ---------------------------------------------------------
    # Error Handlers
    # ---------------------------------------------------------
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('index.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return jsonify({'error': 'An internal server error occurred'}), 500

    return app


# Application entry point instance for WSGI servers (Gunicorn / uWSGI)
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() in ('true', '1', 't')
    app.run(host=host, port=port, debug=debug_mode)
