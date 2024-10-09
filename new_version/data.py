from app2_final_version import db, Role, Permission, User, Course, bcrypt, app

# Asegurarse de que las operaciones se realizan dentro del contexto de la aplicación
with app.app_context():
    # Crear Roles
    admin_role = Role(name='admin')
    user_role = Role(name='user')

    # Añadir los roles a la sesión de la base de datos
    db.session.add(admin_role)
    db.session.add(user_role)

    # Crear Permisos
    read_permission = Permission(name='read')
    write_permission = Permission(name='write')
    edit_permission = Permission(name='edit')

    # Añadir los permisos a la sesión de la base de datos
    db.session.add(read_permission)
    db.session.add(write_permission)
    db.session.add(edit_permission)

    # Asociar roles con permisos
    admin_role.permissions.append(read_permission)
    admin_role.permissions.append(write_permission)
    admin_role.permissions.append(edit_permission)

    user_role.permissions.append(read_permission)

    # Crear Usuarios con sus roles
    admin_user = User(username='admin', password_hash=bcrypt.generate_password_hash('adminpass').decode('utf-8'), role='admin')
    normal_user = User(username='user1', password_hash=bcrypt.generate_password_hash('userpass').decode('utf-8'), role='user')

    # Añadir los usuarios a la sesión de la base de datos
    db.session.add(admin_user)
    db.session.add(normal_user)

    # Crear Cursos
    course1 = Course(title='Advanced Python', description='Learn advanced Python concepts', instructor='Dr. John Smith', duration=40, enrollment_limit=30)
    course2 = Course(title='Machine Learning', description='Introduction to Machine Learning', instructor='Jane Doe', duration=50, enrollment_limit=25)
    course3 = Course(title='Cybersecurity Basics', description='Learn the basics of cybersecurity', instructor='Alan Turing', duration=60, enrollment_limit=20)

    # Añadir los cursos a la sesión de la base de datos
    db.session.add(course1)
    db.session.add(course2)
    db.session.add(course3)

    # Guardar todos los cambios en la base de datos
    db.session.commit()

print("Roles, Permissions, Users, and Courses added successfully.")
