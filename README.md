# Secure MCP (Master Control Program)

A secure implementation for AI-assisted command line interactions.

## Features

- Secure command execution with validation
- Whitelist-based command filtering
- Client-server architecture
- Timeout protection

## Usage

1. Start the server:
```bash
python server.py
```

2. Connect with the client:
```bash
python client.py
```

## Security

- Only whitelisted commands are allowed
- Command validation and sanitization
- Network isolation
- Execution timeouts

## Configuration

Edit the `allowed_commands` list in `server.py` to modify permitted commands.