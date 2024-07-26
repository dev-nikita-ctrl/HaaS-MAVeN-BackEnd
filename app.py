# from flask import Flask,render_template,url_for,redirect,request
# from pymongo import MongoClient

from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)


client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
users_collection = db['users']
projects_collection = db['projects']
hardware_collection = db['hardware']


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def check_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if 'name' in data and 'email' in data and 'password' in data:
        hashed_password = hash_password(data['password'])
        user = {
            "name": data['name'],
            "email": data['email'],
            "password": hashed_password
        }
        users_collection.insert_one(user)
        return jsonify({"message": "User created successfully"}), 201
    else:
        return jsonify({"error": "Invalid input"}), 400


@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    if 'email' in data and 'password' in data:
        user = users_collection.find_one({"email": data['email']})
        if user and check_password(user['password'], data['password']):
            return jsonify({"message": "Sign in successful"}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    else:
        return jsonify({"error": "Invalid input"}), 400


@app.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    if 'name' in data and 'description' in data:
        project = {
            "name": data['name'],
            "description": data['description']
        }
        result = projects_collection.insert_one(project)
        return jsonify({"message": "Project created", "id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid input"}), 400

# # Hardware check-in and check-out route
# @app.route('/hardware', methods=['POST'])
# def manage_hardware():
#     data = request.get_json()
#     if 'project_id' in data and 'action' in data and 'hardware_id' in data:
#         project_id = data['project_id']
#         action = data['action']
#         hardware_id = data['hardware_id']

#         if action not in ['check_in', 'check_out']:
#             return jsonify({"error": "Invalid action"}), 400

#         hardware = hardware_collection.find_one({"hardware_id": hardware_id})
#         if action == 'check_in':
#             if hardware and hardware['status'] == 'checked_out':
#                 hardware_collection.update_one({"hardware_id": hardware_id}, {"$set": {"status": "available", "project_id": None}})
#                 return jsonify({"message": "Hardware checked in"}), 200
#             else:
#                 return jsonify({"error": "Hardware not checked out"}), 400
#         elif action == 'check_out':
#             if hardware and hardware['status'] == 'available':
#                 hardware_collection.update_one({"hardware_id": hardware_id}, {"$set": {"status": "checked_out", "project_id": project_id}})
#                 return jsonify({"message": "Hardware checked out"}), 200
#             else:
#                 return jsonify({"error": "Hardware not available"}), 400
#     else:
#         return jsonify({"error": "Invalid input"}), 400

if __name__ == '__main__':
    app.run(debug=True)

