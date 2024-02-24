from datetime import datetime, timedelta
import asyncio
import random


class QueueManager:
    def __init__(self):
        self.queue = ["IHasPeks"]  # Main queue
        self.overflow_queue = []  # Overflow queue
        self.not_available = {}
        self.team_size = 5  # Default team size
        self.max_main_queue_size = 2  # Maximum number of people in the main queue

    def set_team_size(self, size):
        self.team_size = size
        return f"Team size set to {size}."

    def join_queue(self, username):
        if username in self.queue or username in self.overflow_queue:
            return f"{username}, you are already in queue."
        
        # If main queue is not full, add to main queue
        if len(self.queue) < self.max_main_queue_size:
            self.queue.append(username)
            return f"{username} joined main queue. Pos: {len(self.queue)}"
        else:
            # Add to overflow queue if main queue is full
            self.overflow_queue.append(username)
            return f"{username} added to overflow queue. Pos: {len(self.overflow_queue)} in overflow"

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
            return f"{username}, you have left the overflow queue."
        else:
            return f"{username}, you were not in any queue."

    def move_from_overflow_to_main(self):
        if self.overflow_queue and len(self.queue) < self.max_main_queue_size:
            moved_user = self.overflow_queue.pop(0)
            self.queue.append(moved_user)
            return f"{moved_user} moved from overflow to main queue."
        return None

    def force_kick(self, username):
        username_lower = username.lower()
        queue_lower = [user.lower() for user in self.queue]
        if username_lower in queue_lower:
            actual_username = self.queue[queue_lower.index(username_lower)]
            self.queue.remove(actual_username)
            self.not_available.pop(username_lower, None)
            return f"{username} kicked from queue."
        return f"{username} not found in queue."

    def force_join(self, username):
        username_lower = username.lower()
        if username_lower not in [user.lower() for user in self.queue]:
            self.queue.append(username)
            return f"{username} forcefully added to the queue."
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
            to_remove = [user for user, time in self.not_available.items() if time <= now]
            for user in to_remove:
                self.leave_queue(user)
            await asyncio.sleep(60)

    def start_cleanup_task(self, loop):
        loop.create_task(self.remove_not_available())

    def shuffle_teams(self):
        if len(self.queue) < self.team_size * 2:
            return "Failed, Not enough players. Is team size set correctly?."
        random.shuffle(self.queue)
        team1, team2 = self.queue[:self.team_size], self.queue[self.team_size:self.team_size*2]
        return f"Team 1: {', '.join(team1)}\nTeam 2: {', '.join(team2)}"
