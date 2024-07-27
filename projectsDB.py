from pymongo import MongoClient

# Database Initialization
client = MongoClient('localhost', 27017)
db = client['haas_system']
projects_collection = db['projects']
users_collection = db['users']
hardware_collection = db['hardware']

def createProject(project_name, description):
    project = {
        'project_name': project_name,
        'description': description,
        'users': [],
        'hardware': {}
    }
    result = projects_collection.insert_one(project)
    return {'status': 'success', 'message': 'Project created successfully', 'project_id': str(result.inserted_id)}

def getProjectInfo(project_id):
    project = projects_collection.find_one({'_id': project_id})
    if project:
        return {'status': 'success', 'project': project}
    else:
        return {'status': 'error', 'message': 'Project not found'}

def getAllHwNames():
    hardware_names = hardware_collection.distinct('hw_name')
    return {'status': 'success', 'hardware_names': hardware_names}

def checkOutHW(user_id, project_id, hw_name, quantity):
    project = projects_collection.find_one({'_id': project_id})
    if project and project.get('users') and user_id in project['users']:
        hw_info = hardware_collection.find_one({'hw_name': hw_name})
        if hw_info and hw_info.get('available_quantity', 0) >= quantity:
            hardware_collection.update_one({'hw_name': hw_name}, {'$inc': {'available_quantity': -quantity}})
            projects_collection.update_one({'_id': project_id}, {'$inc': {f'hardware.{hw_name}': quantity}})
            return {'status': 'success', 'message': 'Hardware checked out successfully'}
        else:
            return {'status': 'error', 'message': 'Insufficient hardware available'}
    else:
        return {'status': 'error', 'message': 'Project or user not found'}

def checkInHW(user_id, project_id, hw_name, quantity):
    project = projects_collection.find_one({'_id': project_id})
    if project and project.get('users') and user_id in project['users']:
        project_hw_quantity = project.get('hardware', {}).get(hw_name, 0)
        if project_hw_quantity >= quantity:
            hardware_collection.update_one({'hw_name': hw_name}, {'$inc': {'available_quantity': quantity}})
            projects_collection.update_one({'_id': project_id}, {'$inc': {f'hardware.{hw_name}': -quantity}})
            return {'status': 'success', 'message': 'Hardware checked in successfully'}
        else:
            return {'status': 'error', 'message': 'Insufficient hardware to check in'}
    else:
        return {'status': 'error', 'message': 'Project or user not found'}