from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS

# Database Initialization
client = MongoClient('localhost', 27017)
db = client['haas_system']
hardware_collection = db['hardware']
projects_collection = db['projects']
users_collection = db['users']

# Ensure indexes are created
hardware_collection.create_index('hw_name', unique=True)
projects_collection.create_index('project_id', unique=True)  # Index on project_id
users_collection.create_index('user_id', unique=True)

# Import database functions
from usersDB import addUser, login, joinProject, getUserProjectsList
from projectsDB import createProject, getProjectInfo, getAllHwNames, checkOutHW, checkInHW
from hardwareDB import createHardwareSet, queryHardwareSet, updateAvailability, requestSpace

app = Flask(__name__)
CORS(app)

# Routes
@app.route('/login', methods=['POST'])
def handle_login():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')
    result = login(user_id, password)
    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify({"error": result.get("message")}), 403


@app.route('/main', methods=['GET'])
def main_portal():
    return "Welcome to the Main Portal"


@app.route('/join_project', methods=['POST'])
def join_project():
    data = request.json
    user_id = data.get('user_id')
    project_id = data.get('project_id')

    if not user_id or not project_id:
        return jsonify({"error": "Missing user_id or project_id"}), 400  # Return HTTP 400 Bad Request

    response = joinProject(user_id, project_id)
    
    if response['status'] == 'success':
        return jsonify(response), 200  # Return HTTP 200 OK
    elif response['status'] == 'error':
        return jsonify(response), 404  # Return HTTP 404 Not Found
    else:
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500  # Return HTTP 500 Internal Server Error

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({"error": "Missing user_id or password"}), 400

    result, status_code = addUser(user_id, password)
    return jsonify(result), status_code

@app.route('/get_user_projects_list', methods=['GET'])
def get_user_projects_list():
    user_id = request.args.get('user_id')
    return jsonify(getUserProjectsList(user_id))

@app.route('/create_project', methods=['POST'])
def create_project():
    data = request.json
    project_id = data.get('project_id')
    project_name = data.get('project_name')
    description = data.get('description')
    if not project_id or not project_name or not description:
        return jsonify({"error": "Missing project_id, project_name, or description"}), 400
    result, status_code = createProject(project_id, project_name, description)
    return jsonify(result), status_code


@app.route('/get_project_info', methods=['GET'])
def get_project_info():
    project_id = request.args.get('project_id')
    response = getProjectInfo(project_id)
    
    if response['status'] == 'success':
        return jsonify(response), 200  # Return HTTP 200 OK
    elif response['status'] == 'error':
        return jsonify(response), 404  # Return HTTP 404 Not Found
    else:
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500  # Return HTTP 500 Internal Server Error

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

    if not all([user_id, project_id, hw_name, quantity]):
        return jsonify({"error": "Missing parameters"}), 400

    result, status_code = checkOutHW(user_id, project_id, hw_name, quantity)
    return jsonify(result), status_code

@app.route('/check_in', methods=['POST'])
def check_in():
    data = request.json
    user_id = data.get('user_id')
    project_id = data.get('project_id')
    hw_name = data.get('hw_name')
    quantity = data.get('quantity')

    if not all([user_id, project_id, hw_name, quantity]):
        return jsonify({"error": "Missing parameters"}), 400

    result, status_code = checkInHW(user_id, project_id, hw_name, quantity)
    return jsonify(result), status_code



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
