from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId


# Database Initialization
client = MongoClient('localhost', 27017)
db = client['haas_system']
users_collection = db['users']
projects_collection = db['projects']

def addUser(user_id, password):
    hashed_password = generate_password_hash(password)
    user = {
        'user_id': user_id,
        'password': hashed_password,
    }
    users_collection.insert_one(user)
    return {'status': 'success', 'message': 'User added successfully'}

def login(user_id, password):
    user = users_collection.find_one({'user_id': user_id})
    if user and check_password_hash(user['password'], password):
        return {'status': 'success', 'message': 'Login successful'}
    else:
        return {'status': 'error', 'message': 'Invalid credentials'}

def joinProject(user_id, project_id):
    print("Entered db call")
    project = projects_collection.find_one({'_id': ObjectId(project_id)})
    if project:
        projects_collection.update_one({'_id': ObjectId(project_id)}, {'$addToSet': {'users': user_id}})
        return {'status': 'success', 'message': 'User added to project successfully'}
    else:
        return {'status': 'error', 'message': 'Project not found'}

def getUserProjectsList(user_id):
    projects = projects_collection.find({'users': user_id})
    project_list = [{'project_id': str(project['_id']), 'project_name': project['project_name']} for project in projects]
    return project_list