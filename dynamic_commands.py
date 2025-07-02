"""
Dynamic command management for the MurphyAI Twitch bot.

This module handles the creation, modification, and execution of user-defined
dynamic commands with proper validation and persistence.
"""
import json
import os
import time
import logging
import asyncio
from typing import Dict, Optional, List, Tuple

# Set up logging
logger = logging.getLogger(__name__)

class DynamicCommandManager:
    """
    Manages dynamic commands for the Twitch bot.
    
    Handles loading, saving, creating, and executing user-defined commands
    with proper validation, backup, and file watching capabilities.
    """
    def __init__(self):
        self.commands: Dict[str, Dict] = {}
        self.commands_file = "dynamic_commands.json"
        self.backup_dir = os.path.join("state", "command_backups")
        self.last_modified_time = 0
        self.command_watcher_task = None

        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)

        self.load_commands()

    def load_commands(self) -> None:
        """Load commands from JSON file if it exists."""
        if os.path.exists(self.commands_file):
            try:
                with open(self.commands_file, "r", encoding='utf-8') as f:
                    data = json.load(f)

                # Convert from old format if needed
                if isinstance(data, dict) and all(isinstance(v, str) for v in data.values()):
                    # Old format - convert to new format
                    self.commands = {
                        k: {
                            "response": v,
                            "aliases": [],
                            "created_at": time.time(),
                            "used_count": 0
                        } for k, v in data.items()
                    }
                    logger.info("Converted command data from old format to new format")
                    self.save_commands()  # Save in new format
                else:
                    # New format
                    self.commands = data

                # Record the last modified time
                self.last_modified_time = os.path.getmtime(self.commands_file)

                logger.info("Loaded %d dynamic commands", len(self.commands))
            except Exception as e:
                logger.error("Error loading commands: %s", e)
                # Create a backup of the corrupted file
                if os.path.exists(self.commands_file):
                    self._create_backup("corrupted")
                self.commands = {}

    def save_commands(self) -> None:
        """Save commands to JSON file with backup."""
        try:
            # Create a backup before saving
            self._create_backup("regular")

            with open(self.commands_file, "w", encoding='utf-8') as f:
                json.dump(self.commands, f, indent=4)

            # Update the last modified time
            self.last_modified_time = os.path.getmtime(self.commands_file)
            logger.info("Saved %d dynamic commands", len(self.commands))
        except Exception as e:
            logger.error("Error saving commands: %s", e)

    def _create_backup(self, backup_type: str) -> None:
        """Create a backup of the commands file"""
        if os.path.exists(self.commands_file):
            try:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_filename = f"commands_{backup_type}_{timestamp}.json"
                backup_path = os.path.join(self.backup_dir, backup_filename)

                # Copy the file content
                with open(self.commands_file, "r", encoding='utf-8') as src, \
                     open(backup_path, "w", encoding='utf-8') as dst:
                    dst.write(src.read())

                # Clean up old backups if there are more than 10
                backup_files = sorted([
                    os.path.join(self.backup_dir, f)
                    for f in os.listdir(self.backup_dir)
                    if f.startswith(f"commands_{backup_type}_")
                ])

                if len(backup_files) > 10:
                    # Delete oldest backups, keeping the 10 most recent
                    for old_file in backup_files[:-10]:
                        os.remove(old_file)

                logger.info("Created %s command backup: %s", backup_type, backup_filename)
            except Exception as e:
                logger.error("Error creating command backup: %s", e)

    def add_command(self, name: str, response: str, aliases: List[str] = None) -> str:
        """Add a new command or update existing one."""
        # Import validation utilities
        from validation_utils import validate_command_name, validate_command_response, sanitize_input

        name = name.lower().strip()

        # Validate command name
        is_valid, error_msg = validate_command_name(name)
        if not is_valid:
            return error_msg

        # Validate and sanitize response
        response = sanitize_input(response)
        is_valid, error_msg = validate_command_response(response)
        if not is_valid:
            return error_msg

        # Prepare command data
        command_data = {
            "response": response,
            "aliases": aliases or [],
            "updated_at": time.time()
        }

        # If the command already exists, preserve its creation time and count
        if name in self.commands:
            command_data["created_at"] = self.commands[name].get("created_at", time.time())
            command_data["used_count"] = self.commands[name].get("used_count", 0)
        else:
            command_data["created_at"] = time.time()
            command_data["used_count"] = 0

        # Handle aliases
        if aliases:
            # Check for conflicts with existing commands
            conflicts = []
            for alias in aliases:
                alias = alias.lower().strip()
                if alias in self.commands and alias != name:
                    conflicts.append(alias)

            if conflicts:
                return f"Cannot add command due to conflicts with existing commands: {', '.join(conflicts)}"

            # Add the aliases
            for alias in aliases:
                alias = alias.lower().strip()
                if alias and alias != name:
                    command_data["aliases"].append(alias)

        # Add or update the command
        self.commands[name] = command_data
        self.save_commands()

        if aliases and command_data["aliases"]:
            return f"Command '{name}' has been added successfully with aliases: {', '.join(command_data['aliases'])}!"
        return f"Command '{name}' has been added successfully!"

    def remove_command(self, name: str) -> str:
        """Remove a command."""
        name = name.lower()
        # First check if it's a main command
        if name in self.commands:
            del self.commands[name]
            self.save_commands()
            return f"Command '{name}' has been removed."

        # Then check if it's an alias
        for cmd_name, cmd_data in self.commands.items():
            if name in cmd_data.get("aliases", []):
                cmd_data["aliases"].remove(name)
                self.save_commands()
                return f"Alias '{name}' has been removed from command '{cmd_name}'."

        return f"Command '{name}' not found."

    def get_command(self, name: str) -> Optional[Tuple[str, str]]:
        """
        Get a command's response.
        Returns tuple of (response, command_name) where command_name is the main command name
        """
        name = name.lower()

        # Check if it's a direct command
        if name in self.commands:
            cmd_data = self.commands[name]
            cmd_data["used_count"] = cmd_data.get("used_count", 0) + 1
            return cmd_data["response"], name

        # Check if it's an alias
        for cmd_name, cmd_data in self.commands.items():
            if name in cmd_data.get("aliases", []):
                cmd_data["used_count"] = cmd_data.get("used_count", 0) + 1
                return cmd_data["response"], cmd_name

        return None

    def list_commands(self) -> str:
        """List all dynamic commands."""
        if not self.commands:
            return "No dynamic commands available."

        # Sort commands by usage count (most used first)
        sorted_commands = sorted(
            self.commands.items(),
            key=lambda x: x[1].get("used_count", 0),
            reverse=True
        )

        # Format commands with their aliases
        command_list = []
        for name, data in sorted_commands:
            if data.get("aliases"):
                command_list.append(f"{name} (aliases: {', '.join(data['aliases'])})")
            else:
                command_list.append(name)

        return "Dynamic commands: " + ", ".join(command_list)

    def get_command_details(self, name: str) -> str:
        """Get detailed information about a command."""
        name = name.lower()

        # Check if it's a direct command or an alias
        cmd_name = name
        cmd_data = None

        if name in self.commands:
            cmd_data = self.commands[name]
        else:
            # Search in aliases
            for main_name, data in self.commands.items():
                if name in data.get("aliases", []):
                    cmd_name = main_name
                    cmd_data = data
                    break

        if not cmd_data:
            return f"Command '{name}' not found."

        # Format creation and update times
        created_at = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(cmd_data.get("created_at", 0))
        )

        updated_at = "Never updated"
        if "updated_at" in cmd_data:
            updated_at = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(cmd_data["updated_at"])
            )

        # Format response (truncate if too long)
        response = cmd_data["response"]
        if len(response) > 50:
            response = response[:47] + "..."

        details = [
            f"Command: {cmd_name}",
            f"Response: {response}",
            f"Used: {cmd_data.get('used_count', 0)} times",
            f"Created: {created_at}",
            f"Updated: {updated_at}"
        ]

        if cmd_data.get("aliases"):
            details.append(f"Aliases: {', '.join(cmd_data['aliases'])}")

        return "\n".join(details)

    def start_command_watcher(self, loop):
        """Start a task to watch for changes to the commands file"""
        if self.command_watcher_task is None:
            self.command_watcher_task = loop.create_task(self._watch_commands_file())
            logger.info("Started command file watcher task")

    async def _watch_commands_file(self):
        """Watch the commands file for changes and reload when needed"""
        while True:
            try:
                if os.path.exists(self.commands_file):
                    mod_time = os.path.getmtime(self.commands_file)
                    # If the file was modified since we last loaded it
                    if mod_time > self.last_modified_time:
                        logger.info("Commands file modified externally, reloading...")
                        self.load_commands()
            except Exception as e:
                logger.error("Error watching commands file: %s", e)

            await asyncio.sleep(5)  # Check every 5 seconds
