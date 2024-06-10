import yaml


def load_config(filename):
    with open(filename, 'r') as file:
        config = yaml.safe_load(file)
    return config


config_data = load_config('config.yaml')


rsa_config = config_data.get('rsa')
if rsa_config is None:
    raise Exception('RSA configuration not found in config.yaml')

private_key = rsa_config.get('private_key')
if private_key is None:
    raise Exception('Private key not found in config.yaml')

public_key = rsa_config.get('public_key')
if public_key is None:
    raise Exception('Public key not found in config.yaml')
