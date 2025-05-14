# 🤖 MCP Emulator Controller

This is a project to study the usage of MCP Server. This MCP Server project can be used to control the Emulator, such as opening an app, closing an app, capturing a screenshot, pressing the screen, dragging the screen.

## ✅ Features

- Get list of devices connected from MumuEmulator or ADB
- Reload ADB server
- Open TCP port
- Get all package name from device
- Open app from package name
- Stop app from package name
- Tap on device with coordinate
- Swipe on device with coordinate
- Screen capture from device

## 📷 Demo Video


## 📋 Requirements

- uv (https://github.com/astral-sh/uv)

## 📦 Installation

```bash
uv pip install -r pyproject.toml
```

## ⚙️ MCP Client config.json (Claude)
```json
{
    "mcpServers": {
        "MCPEmulatorController": {
            "command": "uv",
            "args": [
                "--directory",
                "path/to/your/project/src",
                "run",
                "main.py"
            ]
        }
    }
}
```

## Make With 🤍 By ZEMONNUB