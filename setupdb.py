from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

# App setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

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

# Function to create the database and populate it with test data
def create_database():
    with app.app_context():
        db.create_all()

        # Crear roles si no existen
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)

        instructor_role = Role.query.filter_by(name='instructor').first()
        if not instructor_role:
            instructor_role = Role(name='instructor')
            db.session.add(instructor_role)

        # Crear permisos si no existen
        permissions = ['view_courses', 'view_course', 'create_course', 'update_course', 'delete_course']
        for perm_name in permissions:
            perm = Permission.query.filter_by(name=perm_name).first()
            if not perm:
                perm = Permission(name=perm_name)
                db.session.add(perm)

        db.session.commit()

        # Asignar todos los permisos al rol admin
        admin_role.permissions = Permission.query.all()

        # Asignar permisos de visualización al rol instructor
        instructor_role.permissions = Permission.query.filter(Permission.name.in_(['view_courses', 'view_course'])).all()

        # Crear un usuario admin si no existe
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', password_hash=bcrypt.generate_password_hash('admin_password').decode('utf-8'), role='admin')
            db.session.add(admin_user)

        # Crear cursos de prueba
        course1 = Course(title='Data Science 101', description='Introduction to data science', instructor='Dr. Smith', duration=40, enrollment_limit=100)
        course2 = Course(title='Machine Learning Basics', description='Learn the fundamentals of machine learning', instructor='Prof. Johnson', duration=50, enrollment_limit=50)
        course3 = Course(title='Python Programming', description='Introductory Python course for beginners', instructor='Ms. Williams', duration=30, enrollment_limit=200)

        db.session.add(course1)
        db.session.add(course2)
        db.session.add(course3)

        db.session.commit()

        print("Database and sample data created successfully!")

# Run the setup
if __name__ == '__main__':
    create_database()
