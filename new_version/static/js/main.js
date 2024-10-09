document.addEventListener("DOMContentLoaded", function() {
    const registerForm = document.getElementById('register-form');
    const loginForm = document.getElementById('login-form');
    const createCourseForm = document.getElementById('create-course-form');
    const deleteCourseForm = document.getElementById('delete-course-form');
    const updateCourseForm = document.getElementById('update-course-form');
    const getCourseForm = document.getElementById('get-course-form');

    let authToken = null;
    let userRole = null;

    // Registro de usuario
    registerForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const username = document.getElementById('register-username').value;
        const password = document.getElementById('register-password').value;
        const role = document.getElementById('role').value;

        fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username, password: password, role: role })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('register-response').innerText = data.msg || 'Usuario registrado exitosamente';
        })
        .catch(error => console.error('Error:', error));
    });

    // Login de usuario
    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username, password: password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.access_token) {
                authToken = data.access_token;
                userRole = data.role;  // Almacena el rol del usuario autenticado
                document.getElementById('login-response').innerText = 'Login exitoso';
                document.getElementById('courses-section').style.display = 'block';

                // Mostrar/Ocultar secciones según el rol del usuario
                if (userRole === 'admin' || userRole === 'editor') {
                    document.getElementById('create-course-section').style.display = 'block';
                    document.getElementById('update-course-section').style.display = 'block';
                }
                if (userRole === 'admin') {
                    document.getElementById('delete-course-section').style.display = 'block';
                }

                fetchCourses(); // Cargar cursos después de iniciar sesión
            } else {
                document.getElementById('login-response').innerText = 'Login fallido';
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Crear un curso
    createCourseForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const title = document.getElementById('course-title').value;
        const description = document.getElementById('course-description').value;
        const instructor = document.getElementById('course-instructor').value;
        const duration = document.getElementById('course-duration').value;
        const enrollment_limit = document.getElementById('course-enrollment-limit').value;

        fetch('/courses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                title: title,
                description: description,
                instructor: instructor,
                duration: duration,
                enrollment_limit: enrollment_limit
            })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('create-course-response').innerText = data.msg || 'Curso creado exitosamente';
            fetchCourses(); // Actualizar la lista de cursos después de crear uno
        })
        .catch(error => console.error('Error:', error));
    });

    // Eliminar un curso
    deleteCourseForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const courseId = document.getElementById('delete-course-id').value;

        fetch(`/courses/${courseId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('delete-course-response').innerText = data.msg || 'Curso eliminado exitosamente';
            fetchCourses(); // Actualizar la lista de cursos después de eliminar uno
        })
        .catch(error => console.error('Error:', error));
    });

    // Actualizar un curso
    updateCourseForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const courseId = document.getElementById('update-course-id').value;
        const title = document.getElementById('update-course-title').value;
        const description = document.getElementById('update-course-description').value;
        const instructor = document.getElementById('update-course-instructor').value;
        const duration = document.getElementById('update-course-duration').value;
        const enrollment_limit = document.getElementById('update-course-enrollment-limit').value;

        fetch(`/courses/${courseId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                title: title,
                description: description,
                instructor: instructor,
                duration: duration,
                enrollment_limit: enrollment_limit
            })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('update-course-response').innerText = data.msg || 'Curso actualizado exitosamente';
            fetchCourses(); // Actualizar la lista de cursos después de actualizar uno
        })
        .catch(error => console.error('Error:', error));
    });

    // Obtener un curso por ID
    getCourseForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const courseId = document.getElementById('get-course-id').value;

        fetch(`/courses/${courseId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        })
        .then(response => response.json())
        .then(data => {
            const courseInfo = `
                <h3>${data.title}</h3>
                <p>${data.description}</p>
                <p><strong>Instructor:</strong> ${data.instructor}</p>
                <p><strong>Duración:</strong> ${data.duration} horas</p>
                <p><strong>Límite de inscripción:</strong> ${data.enrollment_limit}</p>
            `;
            document.getElementById('get-course-response').innerHTML = courseInfo;
        })
        .catch(error => console.error('Error:', error));
    });

    // Obtener la lista de cursos
    function fetchCourses() {
        fetch('/courses', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        })
        .then(response => response.json())
        .then(courses => {
            const coursesList = document.getElementById('courses-list');
            coursesList.innerHTML = ''; // Limpiar la lista antes de agregar nuevos cursos

            courses.forEach(course => {
                const courseElement = document.createElement('div');
                courseElement.innerHTML = `
                    <h3>${course.title}</h3>
                    <p>${course.description}</p>
                    <p><strong>Instructor:</strong> ${course.instructor}</p>
                    <p><strong>Duración:</strong> ${course.duration} horas</p>
                    <p><strong>Límite de inscripción:</strong> ${course.enrollment_limit}</p>
                `;
                coursesList.appendChild(courseElement);
            });
        })
        .catch(error => console.error('Error:', error));
    }
});
