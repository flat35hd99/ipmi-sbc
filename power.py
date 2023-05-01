import os
import time
import hashlib
import hmac
import base64
import uuid
import requests
import argparse
import sys

class SwitchBot():
    def __init__(self, token: str, secret: str):
        self.token = token
        self.secret = secret
        self.endpoint_url = 'https://api.switch-bot.com/v1.1'

    def create_header(self):
        h = {}
        nonce = uuid.uuid4()
        t = int(round(time.time() * 1000))
        string_to_sign = '{}{}{}'.format(self.token, t, nonce)

        string_to_sign = bytes(string_to_sign, 'utf-8')
        secret = bytes(self.secret, 'utf-8')

        sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())
        
        h['Authorization'] = self.token
        h['Content-Type'] = 'application/json'
        h['charset'] = 'utf8'
        h['t'] = str(t)
        h['sign'] = sign
        h['nonce'] = str(nonce)
        
        return h

    def exec_command(self, device_id: str, command: str):
        return requests.post(
            self.endpoint_url + '/devices/' + device_id + '/commands',
            headers=self.create_header(),
            json={"command": command}
        )

    def power_on(self, device_id: str):
        res = self.exec_command(device_id, 'turnOn')
        if not res.ok:
            print("Request failed: ", res.reason)

    def power_off(self, device_id: str):
        res = self.exec_command(device_id, 'turnOff')
        if not res.ok:
            print("Request failed: ", res.reason)

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='SwitchBot API client')
    parser.add_argument('command', choices=['on', 'off', 'reboot'], help='Command to execute')
    args = parser.parse_args(sys.argv[1:])
    
    # Read environment variables or .env file
    envs = read_env()
    token = envs['token']
    secret = envs['secret']
    device_id = envs['device_id']

    client = SwitchBot(token, secret)

    # Execute command
    if args.command == 'on':
        client.power_on(device_id)
    elif args.command == 'off':
        client.power_off(device_id)
    elif args.command == 'reboot':
        client.power_off(device_id)
        client.power_on(device_id)
    else:
        print("Unknown command: ", args.command)

def read_env():
    def get_env_value(key: str):
        if os.path.exists('.env'):
            with open('.env') as f:
                for line in f:
                    if line.startswith(key):
                        return line.split('=')[1].strip()
        return os.environ.get(key)

    token = get_env_value('SWITCHBOT_API_TOKEN')
    secret = get_env_value('SWITCHBOT_API_SECRET')
    device_id = get_env_value('SWITCHBOT_DEVICE_ID')
    
    return {
        "token": token,
        "secret": secret,
        "device_id": device_id,
    }

if __name__ == "__main__":
    main()
