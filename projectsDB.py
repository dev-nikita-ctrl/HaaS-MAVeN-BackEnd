from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
mongo_uri = os.getenv('MONGO_URI')

# Database Initialization
client = MongoClient(mongo_uri)
db = client['haas_system']
projects_collection = db['projects']
users_collection = db['users']
hardware_collection = db['hardware']

def createProject(project_id, project_name, description):
    existing_project = projects_collection.find_one({'project_id': project_id})
    if existing_project:
        return {'status': 'error', 'message': 'Project ID already exists'}, 409
    project = {
        'project_id': project_id,
        'project_name': project_name,
        'description': description,
        'users': [],
        'hardware': {}
    }
    projects_collection.insert_one(project)
    return {'status': 'success', 'message': 'Project created successfully'}, 201



def getProjectInfo(project_id):
    project = projects_collection.find_one({'project_id': project_id})
    if project:
        project['_id'] = str(project['_id'])
        return {'status': 'success', 'project': project}
    else:
        return {'status': 'error', 'message': 'Project not found'}
    

def getAllHwNames():
    hardware_names = hardware_collection.distinct('hw_name')
    return {'status': 'success', 'hardware_names': hardware_names}

def checkOutHW(user_id, project_id, hw_name, quantity):
    project = projects_collection.find_one({'project_id': project_id})
    if not project:
        return {'status': 'error', 'message': 'Project not found'}, 404

    if user_id not in project.get('users', []):
        return {'status': 'error', 'message': 'User not part of the project'}, 403

    hw_info = hardware_collection.find_one({'hw_name': hw_name})
    if not hw_info:
        return {'status': 'error', 'message': 'Hardware set not found'}, 404

    if hw_info.get('available_quantity', 0) < quantity:
        return {'status': 'error', 'message': 'Insufficient hardware available'}, 400

    hardware_collection.update_one({'hw_name': hw_name}, {'$inc': {'available_quantity': -quantity}})
    projects_collection.update_one({'project_id': project_id}, {'$inc': {f'hardware.{hw_name}': quantity}})
    return {'status': 'success', 'message': 'Hardware checked out successfully'}, 200

def checkInHW(user_id, project_id, hw_name, quantity):
    project = projects_collection.find_one({'project_id': project_id})
    if not project:
        return {'status': 'error', 'message': 'Project not found'}, 404

    if user_id not in project.get('users', []):
        return {'status': 'error', 'message': 'User not part of the project'}, 403

    hw_info = hardware_collection.find_one({'hw_name': hw_name})
    if not hw_info:
        return {'status': 'error', 'message': 'Hardware set not found'}, 404

    project_hw_quantity = project.get('hardware', {}).get(hw_name, 0)
    if project_hw_quantity < quantity:
        return {'status': 'error', 'message': 'Insufficient hardware to check in'}, 400

    hardware_collection.update_one({'hw_name': hw_name}, {'$inc': {'available_quantity': quantity}})
    projects_collection.update_one({'project_id': project_id}, {'$inc': {f'hardware.{hw_name}': -quantity}})
    return {'status': 'success', 'message': 'Hardware checked in successfully'}, 200

