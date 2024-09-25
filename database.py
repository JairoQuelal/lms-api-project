from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

# Configuración de la aplicación
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Modelos
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

# Función para poblar la base de datos
def populate_db():
    with app.app_context():
        db.create_all()

        # Crear roles si no existen
        roles = ['admin', 'instructor', 'student']
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name)
                db.session.add(role)

        db.session.commit()

        # Crear permisos si no existen
        permissions = ['view_courses', 'view_course', 'create_course', 'update_course', 'delete_course']
        for perm_name in permissions:
            perm = Permission.query.filter_by(name=perm_name).first()
            if not perm:
                perm = Permission(name=perm_name)
                db.session.add(perm)

        db.session.commit()

        # Asignar permisos a roles
        admin_role = Role.query.filter_by(name='admin').first()
        instructor_role = Role.query.filter_by(name='instructor').first()
        student_role = Role.query.filter_by(name='student').first()

        # Asignar todos los permisos al rol de admin
        admin_role.permissions = Permission.query.all()

        # Asignar permisos limitados al rol de instructor
        instructor_role.permissions = Permission.query.filter(Permission.name.in_(['view_courses', 'view_course'])).all()

        # Asignar permisos solo para ver cursos al rol de estudiante
        student_role.permissions = Permission.query.filter(Permission.name.in_(['view_courses'])).all()

        db.session.commit()

        # Crear usuarios si no existen
        users = [
            {'username': 'admin', 'password': 'admin_password', 'role': 'admin'},
            {'username': 'instructor1', 'password': 'instructor_password', 'role': 'instructor'},
            {'username': 'student1', 'password': 'student_password', 'role': 'student'},
            {'username': 'student2', 'password': 'student_password', 'role': 'student'}
        ]
        
        for user_data in users:
            user = User.query.filter_by(username=user_data['username']).first()
            if not user:
                user = User(
                    username=user_data['username'],
                    password_hash=bcrypt.generate_password_hash(user_data['password']).decode('utf-8'),
                    role=user_data['role']
                )
                db.session.add(user)

        db.session.commit()

        # Crear cursos si no existen
        courses = [
            {'title': 'Introduction to Programming', 'description': 'Learn the basics of programming.', 'instructor': 'John Doe', 'duration': 40, 'enrollment_limit': 30},
            {'title': 'Data Structures and Algorithms', 'description': 'Deep dive into data structures and algorithms.', 'instructor': 'Jane Smith', 'duration': 60, 'enrollment_limit': 25},
            {'title': 'Database Systems', 'description': 'Introduction to database systems and SQL.', 'instructor': 'Alice Johnson', 'duration': 50, 'enrollment_limit': 20},
            {'title': 'Web Development', 'description': 'Learn to build modern web applications.', 'instructor': 'Bob Brown', 'duration': 45, 'enrollment_limit': 35}
        ]

        for course_data in courses:
            course = Course.query.filter_by(title=course_data['title']).first()
            if not course:
                course = Course(**course_data)
                db.session.add(course)

        db.session.commit()

if __name__ == '__main__':
    populate_db()
