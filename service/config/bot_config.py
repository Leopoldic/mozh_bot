from service.additional_functions.read_yaml import read_config

config = read_config()
TOKEN = config.get('TOKEN', {})
PROXIE = config.get('PROXIE')