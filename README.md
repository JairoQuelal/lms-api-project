
# LMS API Project

This project is a RESTful API for managing Learning Management System (LMS) functionality. It allows users to perform various operations related to courses, users, and permissions in the LMS, using a secure and efficient structure with role-based access control.

## Key Features

- **CRUD Operations for Courses**: Create, read, update, and delete courses.
- **Role-Based Access Control (RBAC)**: Users are assigned roles (admin, instructor, etc.) and permissions, ensuring that actions are restricted based on role.
- **Rate Limiting**: To prevent abuse, each endpoint is protected by rate limits using Flask-Limiter.
- **Audit Logging**: Every action (create, update, delete) is logged for tracking user activities.
- **Basic Authentication**: HTTP Basic Authentication is used, secured with password hashing via Flask-Bcrypt.
- **User and Role Management**: Admin can create users, assign roles, and manage permissions.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/JairoQuelal/lms-api-project.git
    cd lms-api-project
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up the database:
    ```bash
    flask db upgrade
    ```

5. Run the application:
    ```bash
    flask run
    ```

## API Endpoints

### Courses
- **GET /courses**: Retrieves a list of all courses (Rate Limit: 30 requests/min).
- **GET /courses/{id}**: Retrieves details of a specific course by ID (Rate Limit: 60 requests/min).
- **POST /courses**: Creates a new course (Rate Limit: 10 requests/min).
- **PUT /courses/{id}**: Updates an existing course (Rate Limit: 10 requests/min).
- **DELETE /courses/{id}**: Deletes a course (Rate Limit: 5 requests/min).

### Users & Roles
- **GET /users**: Retrieves all users.
- **POST /users**: Create a new user with a specified role.
- **POST /roles**: Creates a new role.
- **POST /roles/{role_id}/permissions**: Assign permissions to a role.

### Authentication
Basic authentication is required for most operations:
```bash
curl -u username:password http://localhost:5000/courses
```

## Security and Authorization
The API supports Role-Based Access Control (RBAC), where each role (e.g., admin, instructor) is associated with specific permissions. For example:
- **Admin**: Can create, update, and delete any course, manage users and roles.
- **Instructor**: Can view courses, create and update their own courses.

## Future Enhancements

- **JWT Authentication**: Currently, the API uses basic auth, but future versions will incorporate JWT for better security.
- **Enhanced Error Handling**: Improve error messages and add error codes for better debugging.
- **Pagination**: Add pagination to endpoints like `GET /courses` to handle large datasets.

## Contribution
Feel free to contribute by submitting pull requests. Ensure that you run all tests before creating a pull request.

## License
This project is licensed under the MIT License.
