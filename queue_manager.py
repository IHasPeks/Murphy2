from datetime import datetime, timedelta
import asyncio
import random


class QueueManager:
    def __init__(self):
        self.queue = ["IHasPeks"]
        self.not_available = {}
        self.team_size = 5  # Default team size

    def set_team_size(self, size):
        self.team_size = size
        return f"Team size set to {size}."

    def join_queue(self, username):
        if username in self.queue:
            return f"{username}, you are already in queue."
        self.queue.append(username)
        return (
            f"{username} joined queue. Pos: {self.queue.index(username) + 1}"
        )

    def leave_queue(self, username):
        if username in self.queue:
            self.queue.remove(username)
            if username in self.not_available:
                del self.not_available[username]
            return f"{username}, you have left queue."
        return f"{username}, you were not in queue."

    def force_kick(self, username):
        username_lower = username.lower()  # Convert to lowercase
        # Check and remove from queue using the lowercase username
        if username_lower in [user.lower() for user in self.queue]:
            self.queue.remove(username_lower)
            # Check and delete from not_available using the lowercase username
            if username_lower in self.not_available:
                del self.not_available[username_lower]
            return f"{username} kicked from queue."
        return f"{username} not found in queue."

    def force_join(self, username):
        username_lower = username.lower()  # Convert to lowercase
        # Check if the lowercase username is not in the lowercase version of the queue
        if username_lower not in [user.lower() for user in self.queue]:
            self.queue.append(username_lower)  # Add the lowercase username
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
            to_remove = [
                user for user, time in self.not_available.items() if time <= now
            ]
            for user in to_remove:
                self.leave_queue(user)
            await asyncio.sleep(60)  # Check every minute

    def start_cleanup_task(self, loop):
        loop.create_task(self.remove_not_available())


    def shuffle_teams(self):
        if len(self.queue) < self.team_size * 2:
            return "Failed, Not enough players. Is team size set correctly?."

        random.shuffle(self.queue)
        team1 = self.queue[:self.team_size]
        team2 = self.queue[self.team_size:self.team_size*2]

        team1_names = ', '.join(team1)
        team2_names = ', '.join(team2)

        response = f"Team 1: {team1_names}\nTeam 2: {team2_names}"
        return response

# prio queue
# mod cmds for q
