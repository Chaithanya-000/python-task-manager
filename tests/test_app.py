"""
Automated Pytest Test Suite for Python Task Manager
Covers application startup, health check, UI routes, and all REST API endpoints.
Uses an isolated in-memory test database so development and production data are untouched.
"""

import json
import tempfile
import os
from models import Task, db
from app import create_app


def test_app_startup_and_config(app):
    """Test that the application starts up correctly with testing config."""
    assert app is not None
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'


def test_health_check_endpoint(client):
    """Verify /health returns HTTP 200 and healthy status for CI/CD checks."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'
    assert 'timestamp' in data


def test_homepage_dashboard(client):
    """Verify the home dashboard page renders successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'TaskMaster' in response.data
    assert b'Workspace Dashboard' in response.data


def test_create_task_success(client):
    """Test adding new tasks with valid data."""
    payload = {
        'title': 'Build Docker Image',
        'description': 'Create minimal Alpine or Slim Python image',
        'priority': 'High',
        'status': 'Pending'
    }
    response = client.post(
        '/api/tasks',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = response.get_json()
    assert 'task' in data
    assert data['task']['title'] == 'Build Docker Image'
    assert data['task']['priority'] == 'High'
    assert data['task']['status'] == 'Pending'
    assert data['task']['id'] is not None


def test_create_task_validation_missing_title(client):
    """Test that creating a task without title returns 400 Bad Request."""
    payload = {
        'title': '   ',
        'description': 'Missing valid title'
    }
    response = client.post(
        '/api/tasks',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'title is required' in data['error']


def test_create_task_validation_invalid_priority(client):
    """Test that providing an invalid priority returns 400 Bad Request."""
    payload = {
        'title': 'Configure Nginx proxy',
        'priority': 'Urgent'  # Invalid priority
    }
    response = client.post(
        '/api/tasks',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Invalid priority' in data['error']


def test_create_task_validation_invalid_status(client):
    """Test that providing an invalid status returns 400 Bad Request."""
    payload = {
        'title': 'Configure SSL certificates',
        'status': 'Archived'  # Invalid status
    }
    response = client.post(
        '/api/tasks',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Invalid status' in data['error']


def test_get_all_tasks(client, sample_task):
    """Test retrieving all tasks."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert 'tasks' in data
    assert data['count'] >= 1
    assert data['tasks'][0]['title'] == sample_task['title']


def test_get_single_task_success(client, sample_task):
    """Test retrieving a specific task by its ID."""
    task_id = sample_task['id']
    response = client.get(f'/api/tasks/{task_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == task_id
    assert data['title'] == sample_task['title']


def test_get_single_task_not_found(client):
    """Test retrieving a non-existent task returns 404."""
    response = client.get('/api/tasks/9999')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data


def test_edit_task_success(client, sample_task):
    """Test updating existing task fields."""
    task_id = sample_task['id']
    update_payload = {
        'title': 'Setup Jenkins CI/CD Pipeline with Webhooks',
        'description': 'Updated description with GitHub Webhook triggers',
        'priority': 'Medium',
        'status': 'Completed'
    }
    response = client.put(
        f'/api/tasks/{task_id}',
        data=json.dumps(update_payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['task']['title'] == 'Setup Jenkins CI/CD Pipeline with Webhooks'
    assert data['task']['priority'] == 'Medium'
    assert data['task']['status'] == 'Completed'


def test_edit_task_invalid_input(client, sample_task):
    """Test updating task with empty title returns 400."""
    task_id = sample_task['id']
    response = client.put(
        f'/api/tasks/{task_id}',
        data=json.dumps({'title': '  '}),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_toggle_task_status(client, sample_task):
    """Test marking task as completed and pending using the status endpoint."""
    task_id = sample_task['id']
    assert sample_task['status'] == 'Pending'

    # Toggle to Completed
    response = client.patch(f'/api/tasks/{task_id}/status')
    assert response.status_code == 200
    data = response.get_json()
    assert data['task']['status'] == 'Completed'

    # Toggle back to Pending
    response2 = client.patch(f'/api/tasks/{task_id}/status')
    assert response2.status_code == 200
    data2 = response2.get_json()
    assert data2['task']['status'] == 'Pending'

    # Explicitly set to Completed
    response3 = client.patch(
        f'/api/tasks/{task_id}/status',
        data=json.dumps({'status': 'Completed'}),
        content_type='application/json'
    )
    assert response3.status_code == 200
    data3 = response3.get_json()
    assert data3['task']['status'] == 'Completed'


def test_delete_task(client, sample_task):
    """Test deleting an existing task."""
    task_id = sample_task['id']
    response = client.delete(f'/api/tasks/{task_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Task deleted successfully.'
    assert data['id'] == task_id

    # Verify task no longer exists
    get_res = client.get(f'/api/tasks/{task_id}')
    assert get_res.status_code == 404


def test_search_tasks_by_title_and_description(client):
    """Test searching tasks by keyword."""
    # Create distinct tasks
    client.post('/api/tasks', json={'title': 'Configure AWS Security Group', 'description': 'Port 80 and 443'})
    client.post('/api/tasks', json={'title': 'Deploy Kubernetes Pod', 'description': 'AWS EKS cluster'})
    client.post('/api/tasks', json={'title': 'Setup Prometheus Monitoring', 'description': 'Metrics collection'})

    # Search for "AWS" - matches 2 tasks
    res = client.get('/api/tasks?search=AWS')
    assert res.status_code == 200
    data = res.get_json()
    assert data['count'] == 2

    # Search for "Prometheus" - matches 1 task
    res2 = client.get('/api/tasks?search=Prometheus')
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2['count'] == 1


def test_filter_tasks_by_status(client):
    """Test filtering tasks by Pending and Completed."""
    client.post('/api/tasks', json={'title': 'Task A', 'status': 'Pending'})
    client.post('/api/tasks', json={'title': 'Task B', 'status': 'Completed'})
    client.post('/api/tasks', json={'title': 'Task C', 'status': 'Completed'})

    res_pending = client.get('/api/tasks?status=Pending')
    data_pending = res_pending.get_json()
    assert data_pending['count'] == 1
    assert data_pending['tasks'][0]['title'] == 'Task A'

    res_completed = client.get('/api/tasks?status=Completed')
    data_completed = res_completed.get_json()
    assert data_completed['count'] == 2


def test_filter_tasks_by_priority(client):
    """Test filtering tasks by Low, Medium, High priority."""
    client.post('/api/tasks', json={'title': 'Urgent Fix', 'priority': 'High'})
    client.post('/api/tasks', json={'title': 'Regular Task', 'priority': 'Medium'})
    client.post('/api/tasks', json={'title': 'Minor Tweaks', 'priority': 'Low'})

    res_high = client.get('/api/tasks?priority=High')
    data_high = res_high.get_json()
    assert data_high['count'] == 1
    assert data_high['tasks'][0]['title'] == 'Urgent Fix'


def test_statistics_endpoint(client):
    """Test calculation of total, completed, pending, and completion percentage."""
    client.post('/api/tasks', json={'title': 'Task 1', 'status': 'Completed', 'priority': 'High'})
    client.post('/api/tasks', json={'title': 'Task 2', 'status': 'Completed', 'priority': 'Medium'})
    client.post('/api/tasks', json={'title': 'Task 3', 'status': 'Pending', 'priority': 'Low'})
    client.post('/api/tasks', json={'title': 'Task 4', 'status': 'Pending', 'priority': 'High'})

    res = client.get('/api/stats')
    assert res.status_code == 200
    stats = res.get_json()

    assert stats['total'] == 4
    assert stats['completed'] == 2
    assert stats['pending'] == 2
    assert stats['completion_percentage'] == 50.0
    assert stats['priority_breakdown']['high'] == 2
    assert stats['priority_breakdown']['medium'] == 1
    assert stats['priority_breakdown']['low'] == 1


def test_cli_seed_and_init(runner):
    """Test the Flask custom CLI commands init-db and seed-db."""
    init_res = runner.invoke(args=['init-db'])
    assert init_res.exit_code == 0
    assert 'Database initialized' in init_res.output

    seed_res = runner.invoke(args=['seed-db'])
    assert seed_res.exit_code == 0
    assert 'Database seeded' in seed_res.output


def test_database_persistence_across_app_restarts():
    """
    Test that database records persist to disk and remain available after restarting the application.
    Simulates application shutdown and relaunch with persistent SQLite storage.
    """
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
        temp_db_path = tf.name

    try:
        os.environ['DATABASE_URL'] = f"sqlite:///{temp_db_path}"

        # 1. First app launch: create task
        app1 = create_app('development')
        with app1.app_context():
            db.create_all()
            task1 = Task(title="Persistent Backup Task", description="Testing persistent disk write", priority="High")
            db.session.add(task1)
            db.session.commit()
            saved_id = task1.id

        # 2. Simulate application restart (new app instance reading same database)
        app2 = create_app('development')
        with app2.app_context():
            loaded_task = db.session.get(Task, saved_id)
            assert loaded_task is not None
            assert loaded_task.title == "Persistent Backup Task"
            assert loaded_task.priority == "High"
            assert loaded_task.status == "Pending"
    finally:
        # Cleanup environment and temporary file
        os.environ.pop('DATABASE_URL', None)
        if os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except PermissionError:
                pass
