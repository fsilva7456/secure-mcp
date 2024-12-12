import socket
import subprocess
import json
import os
from typing import List, Dict

class MCPServer:
    def __init__(self, host='localhost', port=65432):
        self.host = host
        self.port = port
        self.allowed_commands: List[str] = ['ls', 'dir', 'pwd']
        
    def validate_command(self, command: str) -> bool:
        base_cmd = command.split()[0]
        return base_cmd in self.allowed_commands
    
    def execute_command(self, command: str) -> Dict:
        if not self.validate_command(command):
            return {'status': 'error', 'output': 'Command not allowed'}
        
        try:
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
            return {'status': 'error', 'output': str(e)}
    
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f'Server listening on {self.host}:{self.port}')
            
            while True:
                conn, addr = s.accept()
                with conn:
                    print(f'Connected by {addr}')
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                            
                        command = data.decode('utf-8')
                        result = self.execute_command(command)
                        conn.sendall(json.dumps(result).encode('utf-8'))

if __name__ == '__main__':
    server = MCPServer()
    server.start()