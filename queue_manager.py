from datetime import datetime, timedelta
import asyncio
import random
import os


class QueueManager:
    def __init__(self):
        # Get default user from environment or use empty queue
        default_user = os.getenv("DEFAULT_QUEUE_USER", "").strip()
        self.queue = [default_user] if default_user else []  # Main queue
        self.overflow_queue = []  # Overflow queue
        self.not_available = {}
        self.team_size = int(os.getenv("DEFAULT_TEAM_SIZE", "5"))  # Default team size
        self.main_queue_size = int(os.getenv("DEFAULT_QUEUE_SIZE", "5"))  # Maximum number of people in the main queue

    def set_team_size(self, size):
        # Validate team size
        from validation_utils import validate_team_size
        is_valid, error_msg = validate_team_size(str(size))
        if not is_valid:
            return error_msg

        self.team_size = int(size)
        return f"Team size set to {self.team_size}."

    def set_main_queue_size(self, size):
        self.main_queue_size = size
        return f"Main queue size set to {size}."

    def join_queue(self, username):
        if username in self.queue or username in self.overflow_queue:
            return f"{username}, you are already in queue."

        # If main queue is not full, add to main queue
        if len(self.queue) < self.main_queue_size:
            self.queue.append(username)
            return f"{username} joined main queue. Pos: {len(self.queue)}"
        else:
            # Add to overflow queue if main queue is full
            self.overflow_queue.append(username)
            return f"{username} main queue full. added to overflow. Pos: {len(self.overflow_queue)} in overflow"

    def leave_queue(self, username):
        if username in self.queue:
            self.queue.remove(username)
            # Move the first person from overflow to main queue if there's space
            if self.overflow_queue:
                moved_user = self.overflow_queue.pop(0)
                self.queue.append(moved_user)
                response = f"{moved_user} moved from overflow to main queue. "
            else:
                response = ""
            response += f"{username}, you have left the queue."
            return response
        elif username in self.overflow_queue:
            self.overflow_queue.remove(username)
            return f"{username}, you left overflow queue."
        else:
            return f"{username}, you were not in any queue."

    def move_from_overflow_to_main(self):
        if self.overflow_queue and len(self.queue) < self.main_queue_size:
            moved_user = self.overflow_queue.pop(0)
            self.queue.append(moved_user)
            return f"{moved_user} moved from overflow to main queue."
        return None

    def move_user_up(self, username):
        if username in self.queue:
            index = self.queue.index(username)
            if index > 0:
                self.queue[index], self.queue[index - 1] = (
                    self.queue[index - 1],
                    self.queue[index],
                )
                return f"{username} moved up in the queue."
        return f"{username} could not be moved up in the queue."

    def move_user_down(self, username):
        if username in self.queue:
            index = self.queue.index(username)
            if index < len(self.queue) - 1:
                self.queue[index], self.queue[index + 1] = (
                    self.queue[index + 1],
                    self.queue[index],
                )
                return f"{username} moved down in the queue."
        return f"{username} could not be moved down in the queue."

    def force_kick(self, username):
        # Validate username
        from validation_utils import validate_username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return f"Invalid username: {error_msg}"

        username_lower = username.lower()
        queue_lower = [user.lower() for user in self.queue]
        if username_lower in queue_lower:
            actual_username = self.queue[queue_lower.index(username_lower)]
            self.queue.remove(actual_username)
            self.not_available.pop(username_lower, None)
            return f"{username} kicked from queue."
        return f"{username} not found in queue."

    def force_join(self, username):
        # Validate username
        from validation_utils import validate_username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return f"Invalid username: {error_msg}"

        username_lower = username.lower()
        if username_lower not in [user.lower() for user in self.queue]:
            self.queue.append(username)
            return f"{username} forcefully added to main queue."
        return f"{username} is already in queue."

    def show_queue(self):
        main_queue_msg = "Main Queue is empty."
        overflow_queue_msg = "Overflow Queue is empty."

        if self.queue:
            main_queue_msg = "Main Queue: " + ", ".join(
                f"{user}{' (not available)' if user in self.not_available else ''}"
                for user in self.queue
            )

        if self.overflow_queue:
            overflow_queue_msg = "Overflow Queue: " + ", ".join(self.overflow_queue)

        return main_queue_msg, overflow_queue_msg

    def make_not_available(self, username):
        if username in self.queue:
            self.not_available[username] = datetime.now() + timedelta(hours=1)
            return f"{username} is marked as away, retype ?here during the hour or you'll be autoremoved."
        return f"{username} is not in queue."

    def make_available(self, username):
        if username in self.not_available:
            del self.not_available[username]
            return f"{username} is marked as here."
        return f"{username} was not marked as not available."

    async def remove_not_available(self):
        while True:
            now = datetime.now()
            to_remove = [
                user for user, time in self.not_available.items() if time <= now
            ]
            for user in to_remove:
                self.leave_queue(user)
            await asyncio.sleep(60)

    def clear_queues(self):
        self.queue.clear()  # Clear the main queue
        self.overflow_queue.clear()  # Clear the overflow queue
        # Add default user if configured
        default_user = os.getenv("DEFAULT_QUEUE_USER", "").strip()
        if default_user:
            self.queue.append(default_user)
        return "All queues have been cleared."

    def start_cleanup_task(self, loop):
        loop.create_task(self.remove_not_available())

    def shuffle_teams(self):
        if len(self.queue) < self.team_size * 2:
            return "Failed, Not enough players. Is team size set correctly?."
        random.shuffle(self.queue)
        team1, team2 = (
            self.queue[: self.team_size],
            self.queue[self.team_size : self.team_size * 2],
        )
        return f"Team 1: {', '.join(team1)}\nTeam 2: {', '.join(team2)}"
