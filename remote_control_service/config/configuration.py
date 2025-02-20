import yaml

with open('/home/pi/menuboard/remote_control_service/config/device.yaml', 'r') as fp:
    device_config = yaml.safe_load(fp)


DEVICE_SETTINGS = {
    'Serial': device_config['device']['Serial']
}

with open('/home/pi/menuboard/remote_control_service/config/menuboard_tokens.yaml', 'r') as fp:
    token_config = yaml.safe_load(fp)

TOKENS = {}

if 'token_1' in token_config.get('tokens', {}):
    TOKENS['token_1'] = token_config['tokens']['token_1']

if 'token_2' in token_config.get('tokens', {}):
    TOKENS['token_2'] = token_config['tokens']['token_2']
