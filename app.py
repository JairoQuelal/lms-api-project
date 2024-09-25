from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
auth = HTTPBasicAuth()

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Models
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    instructor = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    enrollment_limit = db.Column(db.Integer)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(50), nullable=False)
    details = db.Column(db.String(500))

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    permissions = db.relationship('Permission', secondary='role_permissions', backref=db.backref('roles', lazy='dynamic'))

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

# Schemas
class CourseSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    instructor = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    duration = fields.Int(required=True, validate=validate.Range(min=1))
    enrollment_limit = fields.Int(validate=validate.Range(min=1))

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

# Authentication
@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        return user

# Permissions
def check_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = auth.current_user()
            role = Role.query.filter_by(name=user.role).first()
            if role and permission in [p.name for p in role.permissions]:
                return f(*args, **kwargs)
            return jsonify({"message": "Permission denied"}), 403
        return decorated_function
    return decorator

# Audit logging
def log_audit(action, details):
    user = auth.current_user()
    audit_log = AuditLog(user_id=user.id, action=action, details=details)
    db.session.add(audit_log)
    db.session.commit()

# Routes
@app.route('/courses', methods=['GET'])
@auth.login_required
@check_permission('view_courses')
@limiter.limit("30 per minute")
def get_courses():
    courses = Course.query.all()
    log_audit('view_courses', 'Retrieved all courses')
    return jsonify(courses_schema.dump(courses)), 200

@app.route('/courses/<int:course_id>', methods=['GET'])
@auth.login_required
@check_permission('view_course')
@limiter.limit("60 per minute")
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    log_audit('view_course', f'Retrieved course with id {course_id}')
    return jsonify(course_schema.dump(course)), 200

@app.route('/courses', methods=['POST'])
@auth.login_required
@check_permission('create_course')
@limiter.limit("10 per minute")
def create_course():
    data = request.json
    errors = course_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    new_course = Course(**data)
    db.session.add(new_course)
    db.session.commit()
    log_audit('create_course', f'Created new course: {new_course.title}')
    return jsonify(course_schema.dump(new_course)), 201

@app.route('/courses/<int:course_id>', methods=['PUT'])
@auth.login_required
@check_permission('update_course')
@limiter.limit("10 per minute")
def update_course(course_id):
    course = Course.query.get_or_404(course_id)
    data = request.json
    errors = course_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    for key, value in data.items():
        setattr(course, key, value)
    db.session.commit()
    log_audit('update_course', f'Updated course with id {course_id}')
    return jsonify(course_schema.dump(course)), 200

@app.route('/courses/<int:course_id>', methods=['DELETE'])
@auth.login_required
@check_permission('delete_course')
@limiter.limit("5 per minute")
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    log_audit('delete_course', f'Deleted course with id {course_id}')
    return '', 204

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create roles if they don't exist
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)
        
        instructor_role = Role.query.filter_by(name='instructor').first()
        if not instructor_role:
            instructor_role = Role(name='instructor')
            db.session.add(instructor_role)
        
        # Create permissions if they don't exist
        permissions = ['view_courses', 'view_course', 'create_course', 'update_course', 'delete_course']
        for perm_name in permissions:
            perm = Permission.query.filter_by(name=perm_name).first()
            if not perm:
                perm = Permission(name=perm_name)
                db.session.add(perm)
        
        db.session.commit()

        # Assign all permissions to admin role
        admin_role.permissions = Permission.query.all()
        
        # Assign view permissions to instructor role
        instructor_role.permissions = Permission.query.filter(Permission.name.in_(['view_courses', 'view_course'])).all()
        
        # Create a default admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', password_hash=bcrypt.generate_password_hash('admin_password').decode('utf-8'), role='admin')
            db.session.add(admin_user)
        
        db.session.commit()
    
    app.run(debug=True)