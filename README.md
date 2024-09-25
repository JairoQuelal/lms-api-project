
# Learning Management System (LMS)

This is a RESTful API for managing course information, built using the Flask framework. It supports basic CRUD operations for courses and includes rate limiting, user authentication, role-based access control (RBAC), and audit logging for security and accountability.

## Features

- **CRUD Operations**: Create, read, update, and delete courses.
- **Rate Limiting**: Limits the number of API requests to prevent abuse.
- **User Authentication**: Uses HTTP Basic Authentication to verify users.
- **Role-Based Access Control (RBAC)**: Permissions are assigned to roles, controlling access to certain actions.
- **Audit Logging**: Logs all actions for tracking and auditing.
- **Data Validation**: Ensures proper formatting and constraints for course details.
  
## Technologies Used

- **Flask**: Web framework for Python.
- **Flask-SQLAlchemy**: ORM for database interactions.
- **Marshmallow**: Data validation and serialization.
- **Flask-Limiter**: Implements rate limiting for API endpoints.
- **Flask-Bcrypt**: Provides password hashing for security.
- **Flask-HTTPAuth**: Basic authentication mechanism.
  
## Endpoints

### Courses

- **GET /courses**
    - Retrieves a list of all courses.
    - Requires the `view_courses` permission.
    - Rate limit: 30 requests/minute.

- **GET /courses/{course_id}**
    - Retrieves a single course by ID.
    - Requires the `view_course` permission.
    - Rate limit: 60 requests/minute.

- **POST /courses**
    - Creates a new course.
    - Requires the `create_course` permission.
    - Rate limit: 10 requests/minute.
    - Example request body:
    ```json
    {
      "title": "Introduction to AI",
      "description": "Learn the basics of AI.",
      "instructor": "John Doe",
      "duration": 10,
      "enrollment_limit": 30
    }
    ```

- **PUT /courses/{course_id}**
    - Updates an existing course.
    - Requires the `update_course` permission.
    - Rate limit: 10 requests/minute.

- **DELETE /courses/{course_id}**
    - Deletes a course by ID.
    - Requires the `delete_course` permission.
    - Rate limit: 5 requests/minute.

### Users

- **GET /users**
    - Retrieves a list of users.
    - Admin only.

- **POST /users**
    - Creates a new user (admin role required).

### Roles

- **GET /roles**
    - Retrieves all roles with their permissions.

- **POST /roles**
    - Creates a new role.

## Authentication

The API uses HTTP Basic Authentication. You must send a valid username and password with each request that requires authentication.

### Example:
```bash
curl -u username:password http://localhost:5000/courses
```

### Role-Based Permissions

- **Admin**: Can view, create, update, and delete courses.
- **Instructor**: Can view courses but cannot modify or delete them.

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/JairoQuelal/lms-api-project.git
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:
    ```bash
    python app.py
    ```

4. Access the API at:
    ```
    http://localhost:5000
    ```

## Database Setup

To initialize the SQLite database, run the following command:
```bash
python db_setup.py
```

This will create the necessary tables and roles (admin, instructor), and an initial admin user.

## Future Improvements

- **JWT Authentication**: Add JSON Web Token (JWT) authentication for more secure, stateless sessions.
- **Pagination**: Implement pagination for large dataset responses.
- **Logging and Monitoring**: Add logging for performance monitoring and issue tracking.
- **Improved Error Handling**: Provide more detailed error messages for API consumers.
  
## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
