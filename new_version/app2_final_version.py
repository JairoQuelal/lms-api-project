from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta

app = Flask(__name__)

from flask import render_template

# Renderiza la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Cambia esto por una clave secreta segura

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Configuración de rate-limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Modelos
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # El campo de rol

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    instructor = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    enrollment_limit = db.Column(db.Integer)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    details = db.Column(db.String(500))
    ip_address = db.Column(db.String(100))

# Función auxiliar para registrar logs
def register_audit_log(user_id, action, details, ip_address):
    audit_log = AuditLog(user_id=user_id, action=action, details=details, ip_address=ip_address)
    db.session.add(audit_log)
    db.session.commit()

# Ruta para registrar usuarios con rol
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    role = request.json.get('role', 'user')  # Asignar el rol proporcionado, o 'user' por defecto

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already taken"}), 400

    if role not in ['admin', 'editor', 'viewer', 'user']:  # Definir los roles permitidos
        return jsonify({"msg": "Invalid role provided"}), 400

    # Crear el hash de la contraseña y crear un nuevo usuario con un rol específico
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password_hash=password_hash, role=role)
    db.session.add(new_user)
    db.session.commit()

    # Registrar el evento en el log
    register_audit_log(new_user.id, "User Registered", f"User '{username}' registered with role '{role}'", request.remote_addr)

    return jsonify({"msg": f"User '{username}' created successfully with role '{role}'!"}), 201

# Ruta para iniciar sesión
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Crear un token JWT que incluye el rol del usuario
    access_token = create_access_token(identity={"username": user.username, "role": user.role})

    # Registrar el evento de login en el log
    register_audit_log(user.id, "User Login", f"User '{username}' logged in", request.remote_addr)

    return jsonify(access_token=access_token, role=user.role)


# Ruta protegida de ejemplo
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    
    # Registrar el acceso a la ruta protegida
    register_audit_log(user.id, "Access Protected Route", f"User accessed protected route", request.remote_addr)
    
    return jsonify(logged_in_as=current_user), 200

# Crear un nuevo curso (solo para admin o editor)
@app.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    current_user = get_jwt_identity()

    if current_user['role'] not in ['admin', 'editor']:  # Solo administradores o editores pueden crear cursos
        return jsonify({"msg": "Admins and Editors only!"}), 403

    data = request.json
    title = data.get('title')
    description = data.get('description')
    instructor = data.get('instructor')
    duration = data.get('duration')
    enrollment_limit = data.get('enrollment_limit')

    new_course = Course(
        title=title,
        description=description,
        instructor=instructor,
        duration=duration,
        enrollment_limit=enrollment_limit
    )
    db.session.add(new_course)
    db.session.commit()

    user = User.query.filter_by(username=current_user['username']).first()
    register_audit_log(user.id, "Course Created", f"Course '{title}' created", request.remote_addr)

    return jsonify({"msg": "Course created successfully"}), 201

# Leer todos los cursos (accesible para todos los roles)
@app.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    courses = Course.query.all()
    courses_list = [{
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "instructor": course.instructor,
        "duration": course.duration,
        "enrollment_limit": course.enrollment_limit
    } for course in courses]

    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    register_audit_log(user.id, "Courses Retrieved", "User retrieved all courses", request.remote_addr)

    return jsonify(courses_list), 200

# Leer un solo curso por ID (accesible para todos los roles)
@app.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    course = Course.query.get(course_id)

    if not course:
        return jsonify({"msg": "Course not found"}), 404

    # Registrar el evento en el log
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    register_audit_log(user.id, "Course Retrieved", f"User retrieved course '{course.title}'", request.remote_addr)

    return jsonify({
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "instructor": course.instructor,
        "duration": course.duration,
        "enrollment_limit": course.enrollment_limit
    }), 200

# Actualizar un curso (solo para admin o editor)
@app.route('/courses/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    current_user = get_jwt_identity()

    if current_user['role'] not in ['admin', 'editor']:  # Solo administradores o editores pueden actualizar cursos
        return jsonify({"msg": "Admins and Editors only!"}), 403

    course = Course.query.get(course_id)

    if not course:
        return jsonify({"msg": "Course not found"}), 404

    data = request.json
    course.title = data.get('title', course.title)
    course.description = data.get('description', course.description)
    course.instructor = data.get('instructor', course.instructor)
    course.duration = data.get('duration', course.duration)
    course.enrollment_limit = data.get('enrollment_limit', course.enrollment_limit)

    db.session.commit()

    user = User.query.filter_by(username=current_user['username']).first()
    register_audit_log(user.id, "Course Updated", f"Course '{course.title}' updated", request.remote_addr)

    return jsonify({"msg": "Course updated successfully"}), 200

# Eliminar un curso (solo para admin)
@app.route('/courses/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    current_user = get_jwt_identity()

    if current_user['role'] != 'admin':  # Solo administradores pueden eliminar cursos
        return jsonify({"msg": "Admins only!"}), 403

    course = Course.query.get(course_id)

    if not course:
        return jsonify({"msg": "Course not found"}), 404

    db.session.delete(course)
    db.session.commit()

    user = User.query.filter_by(username=current_user['username']).first()
    register_audit_log(user.id, "Course Deleted", f"Course '{course.title}' deleted", request.remote_addr)

    return jsonify({"msg": "Course deleted successfully"}), 200

# Iniciar la aplicación y crear las tablas si no existen
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear todas las tablas
    app.run(debug=True)
