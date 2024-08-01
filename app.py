

from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

# Database Initialization
client = MongoClient('localhost', 27017)
db = client['haas_system']
hardware_collection = db['hardware']
projects_collection = db['projects']
users_collection = db['users']

# Ensure indexes are created
hardware_collection.create_index('hw_name', unique=True)
projects_collection.create_index('project_name', unique=True)
users_collection.create_index('user_id', unique=True)

# Import database functions
from usersDB import addUser, login, joinProject, getUserProjectsList
from projectsDB import createProject, getProjectInfo, getAllHwNames, checkOutHW, checkInHW
from hardwareDB import createHardwareSet, queryHardwareSet, updateAvailability, requestSpace

app = Flask(__name__)

# Routes
@app.route('/login', methods=['POST'])
def handle_login():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')
    return jsonify(login(user_id, password))

@app.route('/main', methods=['GET'])
def main_portal():
    return "Welcome to the Main Portal"

@app.route('/join_project', methods=['POST'])
def join_project():
    data = request.json
    user_id = data.get('user_id')
    project_id = data.get('project_id')
    return jsonify(joinProject(user_id, project_id))
    # user logged in must also join the project
    # get user projects ( from that get project id)
    # user exists in project on multiple requests

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')
    return jsonify(addUser(user_id, password))

@app.route('/get_user_projects_list', methods=['GET'])
def get_user_projects_list():
    user_id = request.args.get('user_id')
    return jsonify(getUserProjectsList(user_id))

@app.route('/create_project', methods=['POST'])
def create_project():
    data = request.json
    project_name = data.get('project_name')
    description = data.get('description')
    return jsonify(createProject(project_name, description))

@app.route('/get_project_info', methods=['GET'])
def get_project_info():
    project_id = request.args.get('project_id')
    return jsonify(getProjectInfo(ObjectId(project_id)))

@app.route('/get_all_hw_names', methods=['GET'])
def get_all_hw_names():
    return jsonify(getAllHwNames())

@app.route('/get_hw_info', methods=['GET'])
def get_hw_info():
    hw_name = request.args.get('hw_name')
    return jsonify(queryHardwareSet(hw_name))

@app.route('/check_out', methods=['POST'])
def check_out():
    data = request.json
    user_id = data.get('user_id')
    project_id = data.get('project_id')
    hw_name = data.get('hw_name')
    quantity = data.get('quantity')
    return jsonify(checkOutHW(user_id, ObjectId(project_id), hw_name, quantity))

@app.route('/check_in', methods=['POST'])
def check_in():
    data = request.json
    user_id = data.get('user_id')
    project_id = data.get('project_id')
    hw_name = data.get('hw_name')
    quantity = data.get('quantity')
    return jsonify(checkInHW(user_id, ObjectId(project_id), hw_name, quantity))

@app.route('/create_hardware_set', methods=['POST'])
def create_hardware_set():
    data = request.json
    hw_name = data.get('hw_name')
    total_quantity = data.get('total_quantity')
    return jsonify(createHardwareSet(hw_name, total_quantity))

@app.route('/api/inventory', methods=['GET'])
def inventory():
    return jsonify(requestSpace())

if __name__ == '__main__':
    app.run(debug=True)
