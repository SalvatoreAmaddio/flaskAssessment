import csv
from flask import Flask, jsonify
from .database import db
from .routes.student import student_blueprint
from .routes.address import address_blueprint
from .routes.user import user_blueprint
from .serialiser import ma
from .security import jwt
from .models.envs import *
from .models.user import User
from .models.student import Student

is_connected = False

db.create_schema(DB_DEFAULT_PATH, DB_NAME)

app = Flask(__name__)

app.register_blueprint(student_blueprint)
app.register_blueprint(address_blueprint)
app.register_blueprint(user_blueprint)

db.set_connection_string(app,DB_PATH)
db.set_app(app)
ma.init_app(app)

jwt.set_secret_key(app,SECRET_KEY)
jwt.set_cookie_security(app,False) #to change to true
jwt.set_token_location(app,["cookies"])
jwt.set_cookie_protection(app)
jwt.set_token_expiration(app)
jwt.set_app(app)

with app.app_context():
        db.create_tables()
        User.create_default_user()
        count = db.record_count(Student)

is_connected = db.check_connection()

@jwt.unauthorized_loader
def missing_token_callback(error_string):
    return jsonify({"msg": "Please login"}), 401

@jwt.expired_token_loader
def custom_expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Your session has expired, please login again."}), 401  

def upload_data():
    if db.record_count(Student) <= 0:
        with open('users.csv', newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(csvreader, None)  # Skip the header row
            for row in csvreader:
                student = Student()
                student.read_CSV_Row(row)
                db.add_new_record(student)
            db.commit()