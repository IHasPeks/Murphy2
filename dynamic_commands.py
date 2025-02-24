import json
import os
from typing import Dict, Optional


class DynamicCommandManager:
    def __init__(self):
        self.commands: Dict[str, str] = {}
        self.commands_file = "dynamic_commands.json"
        self.load_commands()

    def load_commands(self) -> None:
        """Load commands from JSON file if it exists."""
        if os.path.exists(self.commands_file):
            try:
                with open(self.commands_file, "r") as f:
                    self.commands = json.load(f)
            except Exception as e:
                print(f"Error loading commands: {e}")
                self.commands = {}

    def save_commands(self) -> None:
        """Save commands to JSON file."""
        try:
            with open(self.commands_file, "w") as f:
                json.dump(self.commands, f, indent=4)
        except Exception as e:
            print(f"Error saving commands: {e}")

    def add_command(self, name: str, response: str) -> str:
        """Add a new command or update existing one."""
        name = name.lower()
        if not name.isalnum():
            return "Command name must be alphanumeric."

        self.commands[name] = response
        self.save_commands()
        return f"Command '{name}' has been added successfully!"

    def remove_command(self, name: str) -> str:
        """Remove a command."""
        name = name.lower()
        if name in self.commands:
            del self.commands[name]
            self.save_commands()
            return f"Command '{name}' has been removed."
        return f"Command '{name}' not found."

    def get_command(self, name: str) -> Optional[str]:
        """Get a command's response."""
        return self.commands.get(name.lower())

    def list_commands(self) -> str:
        """List all dynamic commands."""
        if not self.commands:
            return "No dynamic commands available."
        return "Dynamic commands: " + ", ".join(self.commands.keys())
