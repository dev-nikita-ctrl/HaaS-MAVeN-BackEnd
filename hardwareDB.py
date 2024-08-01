from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['haas_system']
hardware_collection = db['hardware']

def createHardwareSet(hw_name, total_quantity):
    hardware = {
        'hw_name': hw_name,
        'total_quantity': total_quantity,
        'available_quantity': total_quantity
    }
    hardware_collection.insert_one(hardware)
    return {'status': 'success', 'message': 'Hardware set created successfully'}

def queryHardwareSet(hw_name):
    hardware = hardware_collection.find_one({'hw_name': hw_name})
    hardware['_id'] = str(hardware['_id'])
    return hardware if hardware else {'status': 'error', 'message': 'Hardware not found'}

def updateAvailability(hw_name, quantity):
    hardware = hardware_collection.find_one({'hw_name': hw_name})
    if hardware:
        hardware_collection.update_one({'hw_name': hw_name}, {'$set': {'available_quantity': quantity}})
        return {'status': 'success', 'message': 'Availability updated successfully'}
    else:
        return {'status': 'error', 'message': 'Hardware not found'}

def requestSpace():
    hardware_list = hardware_collection.find()
    return list(hardware_list)

def getAllHwNames():
    hardware_list = hardware_collection.find()
    hw_names = [hardware['hw_name'] for hardware in hardware_list]
    return hw_names
