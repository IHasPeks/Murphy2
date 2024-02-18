class QueueManager:
    def __init__(self):
        self.queue = []
        self.available_users = []

    def join_queue(self, user):
        if user not in self.queue:
            self.queue.append(user)
            return f"{user} has joined the queue."
        else:
            return f"{user} is already in the queue."

    def leave_queue(self, user):
        if user in self.queue:
            self.queue.remove(user)
            self.make_not_available(
                user
            )  # Automatically make a user not available when they leave the queue
            return f"{user} has left the queue."
        else:
            return f"{user} is not in the queue."

    def show_queue(self):
        if self.queue:
            return "Queue: " + ", ".join(self.queue)
        else:
            return "The queue is currently empty."

    def make_available(self, user):
        if user in self.queue and user not in self.available_users:
            self.available_users.append(user)
            return f"{user} is now available."
        elif user in self.available_users:
            return f"{user} is already marked as available."
        else:
            return f"{user} is not in the queue."

    def make_not_available(self, user):
        if user in self.available_users:
            self.available_users.remove(user)
            return f"{user} is now not available."
        else:
            return f"{user} was not available or is not in the queue."

    def get_available_users(self):
        if self.available_users:
            return "Available users: " + ", ".join(self.available_users)
        else:
            return "There are no available users at the moment."


# Example usage
if __name__ == "__main__":
    qm = QueueManager()
    print(qm.join_queue("user1"))
    print(qm.join_queue("user2"))
    print(qm.show_queue())
    print(qm.make_available("user1"))
    print(qm.get_available_users())
    print(qm.leave_queue("user1"))
    print(qm.show_queue())
