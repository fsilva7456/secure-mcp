import socket
import subprocess
import json
import os
import yaml
from typing import List, Dict
from loguru import logger

class ClaudeMCP:
    def __init__(self, config_path='config.yaml'):
        self.load_config(config_path)
        self.setup_logging()
        
    def load_config(self, config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            self.host = config['server']['host']
            self.port = config['server']['port']
            self.allowed_commands = config['commands']['allowed']
            self.blocked_commands = config['commands']['blocked']
    
    def setup_logging(self):
        logger.add('claude_mcp.log', rotation='500 MB')
    
    def validate_command(self, command: str) -> bool:
        base_cmd = command.split()[0]
        return (base_cmd in self.allowed_commands and
                base_cmd not in self.blocked_commands)
    
    def execute_command(self, command: str) -> Dict:
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
    
    def handle_claude_request(self, command: str) -> Dict:
        """Endpoint for Claude to execute commands"""
        try:
            result = self.execute_command(command)
            logger.info(f'Claude command result: {result}')
            return result
        except Exception as e:
            logger.error(f'Claude error: {str(e)}')
            return {'status': 'error', 'output': str(e)}

# Example usage:
def main():
    mcp = ClaudeMCP()
    result = mcp.handle_claude_request('ls')
    print(result)

if __name__ == '__main__':
    main()