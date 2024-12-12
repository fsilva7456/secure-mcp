import socket
import json
from cryptography.fernet import Fernet

class MCPClient:
    def __init__(self, host='localhost', port=65432, auth_token=None):
        self.host = host
        self.port = port
        self.auth_token = auth_token
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self):
        self.socket.connect((self.host, self.port))
        self.key = self.socket.recv(1024)
        self.cipher_suite = Fernet(self.key)
    
    def send_command(self, command: str) -> dict:
        command_data = {
            'command': command,
            'auth_token': self.auth_token
        }
        encrypted = self.cipher_suite.encrypt(json.dumps(command_data).encode('utf-8'))
        self.socket.sendall(encrypted)
        
        response = self.socket.recv(1024)
        decrypted = self.cipher_suite.decrypt(response)
        return json.loads(decrypted.decode('utf-8'))
    
    def close(self):
        self.socket.close()

def main():
    # Read auth token from environment or config
    auth_token = 'your_secure_token_here'  # Replace with your token
    client = MCPClient(auth_token=auth_token)
    
    try:
        client.connect()
        print('Connected to MCP server')
        print('Available commands:', ['ls', 'dir', 'pwd', 'cd', 'echo', 'cat', 'type'])
        
        while True:
            command = input('MCP> ')
            if command.lower() == 'exit':
                break
                
            result = client.send_command(command)
            print(f"Status: {result['status']}")
            if result['output']:
                print(f"Output:\n{result['output']}")
            if result.get('error'):
                print(f"Error:\n{result['error']}")
    
    finally:
        client.close()

if __name__ == '__main__':
    main()