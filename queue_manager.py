from datetime import datetime, timedelta
import asyncio
import random


class QueueManager:
    def __init__(self):
        self.queue = ["IHasPeks"]
        self.not_available = {}
        self.team_size = 5

    def set_team_size(self, size):
        self.team_size = size
        return f"Team size set to {size}."

    def join_queue(self, username):
        if username in self.queue:
            return f"{username}, you are already in queue."
        self.queue.append(username)
        return f"{username} joined queue. Pos: {len(self.queue)}"

    def leave_queue(self, username):
        if username in self.queue:
            self.queue.remove(username)
            self.not_available.pop(username, None)
            return f"{username}, you have left queue."
        return f"{username}, you were not in queue."

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
        if not self.queue:
            return "Queue is empty."
        queue_status = "Queue: " + ", ".join(
            f"{user}{' (not available)' if user in self.not_available else ''}"
            for user in self.queue
        )
        return queue_status

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
