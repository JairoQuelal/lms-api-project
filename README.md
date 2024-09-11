# Learning Management System API

This project implements a RESTful API for a Learning Management System (LMS) using Flask. It includes basic CRUD operations for managing courses, along with rate limiting to prevent abuse.

## Features

- CRUD operations for courses (Create, Read, Update, Delete)
- Data validation using Marshmallow
- Rate limiting to prevent API abuse
- SQLite database for data storage

## Requirements

- Python 3.7+
- Flask
- Flask-SQLAlchemy
- Marshmallow
- Flask-Limiter

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/lms-api-project.git
   cd lms-api-project
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Flask application:
   ```
   python app.py
   ```

2. The API will be available at `http://localhost:5000`

3. Use the following endpoints:
   - GET /courses - Retrieve all courses
   - GET /courses/{id} - Retrieve a specific course
   - POST /courses - Create a new course
   - PUT /courses/{id} - Update an existing course
   - DELETE /courses/{id} - Delete a course

## Testing

To test the rate limiting functionality, run:

```
python test_rate_limit.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
