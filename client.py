import socket
import json

class MCPClient:
    def __init__(self, host='localhost', port=65432):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self):
        self.socket.connect((self.host, self.port))
    
    def send_command(self, command: str) -> dict:
        self.socket.sendall(command.encode('utf-8'))
        data = self.socket.recv(1024)
        return json.loads(data.decode('utf-8'))
    
    def close(self):
        self.socket.close()

def main():
    client = MCPClient()
    try:
        client.connect()
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