from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses1.db'
db = SQLAlchemy(app)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    instructor = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    enrollment_limit = db.Column(db.Integer)

class CourseSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    instructor = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    duration = fields.Int(required=True, validate=validate.Range(min=1))
    enrollment_limit = fields.Int(validate=validate.Range(min=1))

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

@app.route('/courses', methods=['GET'])
@limiter.limit("30 per minute")
def get_courses():
    courses = Course.query.all()
    return jsonify(courses_schema.dump(courses)), 200

@app.route('/courses/<int:course_id>', methods=['GET'])
@limiter.limit("60 per minute")
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify(course_schema.dump(course)), 200

@app.route('/courses', methods=['POST'])
@limiter.limit("10 per minute")
def create_course():
    data = request.json
    errors = course_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    new_course = Course(**data)
    db.session.add(new_course)
    db.session.commit()
    return jsonify(course_schema.dump(new_course)), 201

@app.route('/courses/<int:course_id>', methods=['PUT'])
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
    return jsonify(course_schema.dump(course)), 200

@app.route('/courses/<int:course_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)