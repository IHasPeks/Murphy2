from datetime import datetime, timedelta
import asyncio


class QueueManager:
    def __init__(self):
        self.queue = []
        self.not_available = {}

    def join_queue(self, username):
        if username in self.queue:
            return f"{username}, you are already in the queue."
        self.queue.append(username)
        return (
            f"{username} joined the queue. Position: {self.queue.index(username) + 1}"
        )

    def leave_queue(self, username):
        if username in self.queue:
            self.queue.remove(username)
            if username in self.not_available:
                del self.not_available[username]
            return f"{username}, you have been removed from the queue."
        return f"{username}, you were not in the queue."

    def show_queue(self):
        if not self.queue:
            return "The queue is currently empty."
        queue_status = "Queue: " + ", ".join(
            f"{user}{' (not available)' if user in self.not_available else ''}"
            for user in self.queue
        )
        return queue_status

    def make_not_available(self, username):
        if username in self.queue:
            self.not_available[username] = datetime.now() + timedelta(hours=1)
            return f"{username} is now marked as not available."
        return f"{username} is not in the queue."

    def make_available(self, username):
        if username in self.not_available:
            del self.not_available[username]
            return f"{username} is now available."
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
