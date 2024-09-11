import requests
import random

BASE_URL = 'http://localhost:5000'

def create_course(title, description, instructor, duration, enrollment_limit):
    course_data = {
        "title": title,
        "description": description,
        "instructor": instructor,
        "duration": duration,
        "enrollment_limit": enrollment_limit
    }
    response = requests.post(f'{BASE_URL}/courses', json=course_data)
    print(f"Create course status code: {response.status_code}")
    if response.status_code == 201:
        print(f"Created course: {response.json()}")
        return response.json()['id']
    else:
        print(f"Failed to create course: {response.text}")
        return None

def get_all_courses():
    response = requests.get(f'{BASE_URL}/courses')
    print(f"Get all courses status code: {response.status_code}")
    if response.status_code == 200:
        courses = response.json()
        print(f"Total courses: {len(courses)}")
        for course in courses:
            print(f"- {course['title']} (ID: {course['id']})")
        return courses
    else:
        print(f"Failed to get courses: {response.text}")
        return []

def get_course(course_id):
    response = requests.get(f'{BASE_URL}/courses/{course_id}')
    print(f"Get course status code: {response.status_code}")
    if response.status_code == 200:
        print(f"Course details: {response.json()}")
    elif response.status_code == 404:
        print(f"Course with id {course_id} not found")
    else:
        print(f"Unexpected status code: {response.status_code}")

def update_course(course_id, title, description, instructor, duration, enrollment_limit):
    updated_data = {
        "title": title,
        "description": description,
        "instructor": instructor,
        "duration": duration,
        "enrollment_limit": enrollment_limit
    }
    response = requests.put(f'{BASE_URL}/courses/{course_id}', json=updated_data)
    print(f"Update course status code: {response.status_code}")
    if response.status_code == 200:
        print(f"Updated course: {response.json()}")
    else:
        print(f"Failed to update course: {response.text}")

def delete_course(course_id):
    response = requests.delete(f'{BASE_URL}/courses/{course_id}')
    print(f"Delete course status code: {response.status_code}")
    if response.status_code == 204:
        print(f"Course with id {course_id} successfully deleted")
    else:
        print(f"Failed to delete course: {response.text}")

def run_tests():
    # Create multiple courses
    course_ids = []
    courses_data = [
        ("Introduction to Python", "Learn the basics of Python programming", "John Doe", 8, 30),
        ("Advanced JavaScript", "Master advanced JS concepts", "Jane Smith", 12, 25),
        ("Data Science Fundamentals", "Introduction to data analysis", "Alice Johnson", 10, 20),
        ("Web Development with Flask", "Build web apps with Flask", "Bob Wilson", 15, 22),
        ("Machine Learning Basics", "Introduction to ML algorithms", "Eve Brown", 14, 18)
    ]
    
    for course_data in courses_data:
        course_id = create_course(*course_data)
        if course_id:
            course_ids.append(course_id)
    
    # Get all courses
    all_courses = get_all_courses()
    
    # Get a specific course
    if course_ids:
        get_course(random.choice(course_ids))
    
    # Update a course
    if course_ids:
        update_course(course_ids[0], "Updated Python Course", "New description for Python course", "John Doe", 10, 35)
    
    # Delete a course
    if len(course_ids) > 1:
        delete_course(course_ids[-1])
    
    # Try to get the deleted course
    if len(course_ids) > 1:
        get_course(course_ids[-1])
    
    # Get all courses again to verify changes
    get_all_courses()

if __name__ == '__main__':
    run_tests()