import yaml

def read_config():
    try:
        with open('config.yml', 'r') as ymlfile:
            data = yaml.safe_load(ymlfile)
        return data
    except FileNotFoundError as e:
        print(f"WARNING: {e}")
        return {}