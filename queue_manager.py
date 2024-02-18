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
            self.make_not_available(user)  # Automatically make a user not available when they leave the queue
            return f"{user} has left the queue."
        else:
            return f"{user} is not in the queue."

    def show_queue(self):
        if self.queue:
            queue_positions = ", ".join([f"{idx+1}. {user}" for idx, user in enumerate(self.queue)])
            return f"Queue: {queue_positions}"
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

# Simulate command processing
def simulate_command_processing():
    qm = QueueManager()
    
    # Simulate commands
    commands = [
        ("join", "user1"),
        ("join", "user2"),
        ("show", None),
        ("available", "user1"),
        ("leave", "user1"),
        ("show", None),
        ("join", "user3"),
        ("available", "user2"),
        ("not_available", "user2"),
        ("show", None),
        ("get_available", None)
    ]
    
    for command, user in commands:
        if command == "join":
            print(qm.join_queue(user))
        elif command == "leave":
            print(qm.leave_queue(user))
        elif command == "show":
            print(qm.show_queue())
        elif command == "available":
            print(qm.make_available(user))
        elif command == "not_available":
            print(qm.make_not_available(user))
        elif command == "get_available":
            print("Available users:", ", ".join(qm.available_users))
        else:
            print(f"Unknown command: {command}")

if __name__ == "__main__":
    simulate_command_processing()


