#!/usr/bin/env python3
"""
TechFlow - Professional Developer Collaboration Platform
A modern web application for team collaboration, project management, and code sharing.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, get_flashed_messages, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from datetime import datetime, timedelta
import logging
import uuid
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'techflow-secret-key-2025-enterprise'

# Create instance directory if it doesn't exist
instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Use absolute path for database
db_path = os.path.join(instance_path, 'techflow.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    """User model for TechFlow platform."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(200))
    bio = db.Column(db.Text)
    role = db.Column(db.String(50), default='developer')  # developer, admin, manager
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_active = db.Column(db.DateTime)
    
    # Relationships
    projects = db.relationship('Project', backref='owner', lazy=True)
    team_memberships = db.relationship('TeamMember', backref='user', lazy=True)
    activities = db.relationship('UserActivity', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    """Project model for collaborative development."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    repository_url = db.Column(db.String(200))
    status = db.Column(db.String(50), default='active')  # active, archived, completed
    visibility = db.Column(db.String(50), default='private')  # private, public, team
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team_members = db.relationship('TeamMember', backref='project', lazy=True)
    tasks = db.relationship('Task', backref='project', lazy=True)
    
    def __repr__(self):
        return f'<Project {self.name}>'

class TeamMember(db.Model):
    """Team membership model."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    role = db.Column(db.String(50), default='member')  # owner, admin, member, viewer
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TeamMember {self.user_id}:{self.project_id}>'

class Task(db.Model):
    """Task model for project management."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='todo')  # todo, in_progress, review, done
    priority = db.Column(db.String(50), default='medium')  # low, medium, high, urgent
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Task {self.title}>'

class UserActivity(db.Model):
    """User activity logging for analytics."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    activity_metadata = db.Column(db.Text)  # JSON string for additional data
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserActivity {self.activity_type}'

# Routes
@app.route('/')
def index():
    """Home page with modern landing design."""
    featured_projects = Project.query.filter_by(visibility='public').limit(6).all()
    stats = {
        'total_users': User.query.count(),
        'total_projects': Project.query.count(),
        'active_projects': Project.query.filter_by(status='active').count()
    }
    return render_template('index.html', featured_projects=featured_projects, stats=stats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with enhanced validation."""
    if request.method == 'POST':
        print(f"=== REGISTER ROUTE CALLED ===")
        print(f"Form data received: {request.form}")
        print(f"Request method: {request.method}")
        print(f"Content type: {request.content_type}")
        
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        
        print(f"Parsed form data:")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Full Name: {full_name}")
        print(f"  Password: {'***' if password else 'None'}")
        print(f"  Confirm Password: {'***' if confirm_password else 'None'}")
        
        # Enhanced form validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        
        if not full_name or len(full_name.strip()) < 2:
            errors.append('Full name is required')
        
        if not email or '@' not in email:
            errors.append('Please enter a valid email address')
        
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            errors.append('Username already exists')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            errors.append('Email already registered')
        
        if errors:
            print(f"Validation errors: {errors}")
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Create new user
        try:
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                full_name=full_name.strip(),
                avatar_url=f"https://ui-avatars.com/api/?name={full_name}&background=6366f1&color=fff"
            )
            db.session.add(new_user)
            db.session.commit()
            
            # Log activity
            activity = UserActivity(
                user_id=new_user.id,
                activity_type='registration',
                description='User registered successfully'
            )
            db.session.add(activity)
            db.session.commit()
            
            print(f"User registered successfully: {new_user.username}")
            flash('Registration successful! Welcome to TechFlow.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with enhanced security."""
    if request.method == 'POST':
        print(f"=== LOGIN ROUTE CALLED ===")
        print(f"Login form data received: {request.form}")
        print(f"Request method: {request.method}")
        print(f"Content type: {request.content_type}")
        
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        print(f"Parsed login data:")
        print(f"  Username: {username}")
        print(f"  Password: {'***' if password else 'None'}")
        print(f"  Remember: {remember}")
        
        if not username or not password:
            print("Login validation failed: missing username or password")
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"User found: {user.username}, checking password...")
            if check_password_hash(user.password_hash, password):
                print(f"Password correct, logging in user: {user.username}")
                session['user_id'] = user.id
                session['user'] = user.username
                session['user_role'] = user.role
                
                # Update last login and activity
                user.last_login = datetime.utcnow()
                user.last_active = datetime.utcnow()
                db.session.commit()
                
                # Log activity
                activity = UserActivity(
                    user_id=user.id,
                    activity_type='login',
                    description='User logged in successfully'
                )
                db.session.add(activity)
                db.session.commit()
                
                flash(f'Welcome back, {user.full_name or user.username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                print(f"Password incorrect for user: {user.username}")
                flash('Invalid username or password', 'error')
        else:
            print(f"No user found with username: {username}")
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Enhanced user dashboard with project overview."""
    if 'user_id' not in session:
        flash('Please login to access your dashboard', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    # Get user's projects
    user_projects = Project.query.filter_by(owner_id=user.id).order_by(Project.updated_at.desc()).limit(5).all()
    
    # Get team memberships
    team_projects = db.session.query(Project).join(TeamMember).filter(
        TeamMember.user_id == user.id
    ).order_by(Project.updated_at.desc()).limit(5).all()
    
    # Get recent activities
    activities = UserActivity.query.filter_by(user_id=user.id).order_by(UserActivity.timestamp.desc()).limit(10).all()
    
    # Get assigned tasks
    assigned_tasks = Task.query.filter_by(assignee_id=user.id).filter(
        Task.status.in_(['todo', 'in_progress'])
    ).order_by(Task.due_date.asc()).limit(5).all()
    
    # Dashboard stats
    stats = {
        'total_projects': len(user_projects) + len(team_projects),
        'active_tasks': len(assigned_tasks),
        'completed_tasks': Task.query.filter_by(assignee_id=user.id, status='done').count(),
        'team_memberships': TeamMember.query.filter_by(user_id=user.id).count()
    }
    
    return render_template('dashboard.html', 
                         user=user, 
                         user_projects=user_projects,
                         team_projects=team_projects,
                         activities=activities,
                         assigned_tasks=assigned_tasks,
                         stats=stats)

@app.route('/projects')
def projects():
    """Projects listing page."""
    if 'user_id' not in session:
        flash('Please login to view projects', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get user's own projects
    own_projects = Project.query.filter_by(owner_id=user.id).all()
    
    # Get team projects
    team_projects = db.session.query(Project).join(TeamMember).filter(
        TeamMember.user_id == user.id
    ).all()
    
    # Get public projects
    public_projects = Project.query.filter_by(visibility='public').limit(10).all()
    
    return render_template('projects.html', 
                         own_projects=own_projects,
                         team_projects=team_projects,
                         public_projects=public_projects)

@app.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    """Create new project."""
    if 'user_id' not in session:
        flash('Please login to create projects', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        print(f"=== NEW PROJECT ROUTE CALLED ===")
        print(f"New project form data received: {request.form}")
        print(f"Request method: {request.method}")
        print(f"Content type: {request.content_type}")
        
        name = request.form.get('name')
        description = request.form.get('description')
        repository_url = request.form.get('repository_url')
        visibility = request.form.get('visibility', 'private')
        project_type = request.form.get('project_type')
        tags = request.form.get('tags')
        
        print(f"Parsed new project data:")
        print(f"  Name: {name}")
        print(f"  Description: {description}")
        print(f"  Repository URL: {repository_url}")
        print(f"  Visibility: {visibility}")
        print(f"  Project Type: {project_type}")
        print(f"  Tags: {tags}")
        
        if not name:
            print("New project validation failed: missing project name")
            flash('Project name is required', 'error')
            return render_template('new_project.html')
        
        try:
            project = Project(
                name=name,
                description=description,
                repository_url=repository_url,
                visibility=visibility,
                owner_id=session['user_id']
            )
            db.session.add(project)
            db.session.commit()
            
            print(f"Project created successfully: {project.name}")
            flash(f'Project "{name}" created successfully!', 'success')
            return redirect(url_for('projects'))
            
        except Exception as e:
            logger.error(f"Project creation error: {e}")
            flash('Failed to create project', 'error')
            db.session.rollback()
    
    return render_template('new_project.html')

@app.route('/profile')
def profile():
    """User profile page."""
    if 'user_id' not in session:
        flash('Please login to view your profile', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    """User logout functionality."""
    if 'user_id' in session:
        # Log activity
        activity = UserActivity(
            user_id=session['user_id'],
            activity_type='logout',
            description='User logged out'
        )
        db.session.add(activity)
        db.session.commit()
    
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/test')
def test():
    """Test route to check database and users."""
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role
        })
    
    return jsonify({
        'message': 'TechFlow is running!',
        'total_users': len(users),
        'users': user_list,
        'test_credentials': {
            'username': 'admin',
            'password': 'admin123'
        }
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'service': 'TechFlow',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'TechFlow',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint for platform statistics."""
    try:
        stats = {
            'total_users': User.query.count(),
            'total_projects': Project.query.count(),
            'active_projects': Project.query.filter_by(status='active').count(),
            'total_tasks': Task.query.count(),
            'completed_tasks': Task.query.filter_by(status='done').count()
        }
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Stats API error: {e}")
        return jsonify({'error': 'Database error'}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return render_template('500.html'), 500

def init_db():
    """Initialize the database with tables and sample data."""
    with app.app_context():
        db.create_all()
        
        # Create sample admin user if no users exist
        if User.query.count() == 0:
            admin_user = User(
                username='admin',
                email='admin@techflow.com',
                password_hash=generate_password_hash('admin123'),
                full_name='TechFlow Admin',
                role='admin',
                is_verified=True,
                avatar_url='https://ui-avatars.com/api/?name=Admin&background=ef4444&color=fff'
            )
            db.session.add(admin_user)
            
            # Create sample project
            sample_project = Project(
                name='TechFlow Platform',
                description='The main TechFlow collaboration platform',
                visibility='public',
                owner_id=1
            )
            db.session.add(sample_project)
            
            db.session.commit()
            logger.info("Database initialized with sample data")
        else:
            logger.info("Database already initialized")

@app.route('/test-flash')
def test_flash():
    """Test endpoint to verify flash messages are working."""
    flash('This is a test success message!', 'success')
    flash('This is a test error message!', 'error')
    flash('This is a test info message!', 'info')
    return redirect(url_for('login'))

@app.route('/flash-debug')
def flash_debug():
    """Debug endpoint to show current flash messages."""
    messages = get_flashed_messages(with_categories=True)
    return jsonify({
        'flash_messages': [{'category': cat, 'message': msg} for cat, msg in messages],
        'total_messages': len(messages)
    })

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )