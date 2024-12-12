import socket
import subprocess
import json
import os
import yaml
from typing import List, Dict
from loguru import logger
from cryptography.fernet import Fernet

class MCPServer:
    def __init__(self, config_path='config.yaml'):
        self.load_config(config_path)
        self.setup_logging()
        self.setup_encryption()
        
    def load_config(self, config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            self.host = config['server']['host']
            self.port = config['server']['port']
            self.allowed_commands = config['commands']['allowed']
            self.blocked_commands = config['commands']['blocked']
            self.max_command_length = config['security']['max_command_length']
            self.auth_token = config['security']['auth_token']
            self.require_auth = config['security']['require_auth']
    
    def setup_logging(self):
        logger.add('mcp.log', rotation='500 MB')
    
    def setup_encryption(self):
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
    
    def validate_command(self, command: str) -> bool:
        if len(command) > self.max_command_length:
            return False
            
        base_cmd = command.split()[0]
        return (base_cmd in self.allowed_commands and
                base_cmd not in self.blocked_commands)
    
    def execute_command(self, command: str, auth_token: str = None) -> Dict:
        if self.require_auth and auth_token != self.auth_token:
            return {'status': 'error', 'output': 'Authentication required'}
            
        if not self.validate_command(command):
            logger.warning(f'Blocked command attempt: {command}')
            return {'status': 'error', 'output': 'Command not allowed'}
        
        try:
            logger.info(f'Executing command: {command}')
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=5
            )
            return {
                'status': 'success',
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            logger.error(f'Command error: {str(e)}')
            return {'status': 'error', 'output': str(e)}
    
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            logger.info(f'Server listening on {self.host}:{self.port}')
            
            while True:
                conn, addr = s.accept()
                with conn:
                    logger.info(f'Connected by {addr}')
                    conn.sendall(self.key)
                    
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                            
                        decrypted = self.cipher_suite.decrypt(data)
                        command_data = json.loads(decrypted)
                        result = self.execute_command(
                            command_data['command'],
                            command_data.get('auth_token')
                        )
                        encrypted_response = self.cipher_suite.encrypt(
                            json.dumps(result).encode('utf-8')
                        )
                        conn.sendall(encrypted_response)

if __name__ == '__main__':
    server = MCPServer()
    server.start()