from twitchio.ext import commands
from commands import handle_command
from scheduler import start_scheduler
from queue_manager import QueueManager
from ai_command import handle_ai_command
from config import (
    TWITCH_TOKEN,
    TWITCH_CLIENT_ID,
    TWITCH_PREFIX,
    TWITCH_INITIAL_CHANNELS,
)


class MurphyAI(commands.Bot):

    def __init__(self):
        super().__init__(
            token=TWITCH_TOKEN,
            client_id=TWITCH_CLIENT_ID,
            prefix=TWITCH_PREFIX,
            initial_channels=TWITCH_INITIAL_CHANNELS,
        )
        self.queue_manager = QueueManager()

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"ID | {self.user_id}")
        await start_scheduler(self)

    async def event_user_ban(self, channel, user):
        await channel.send(f"Joeler {user.name} will be missed. KEKBye")

    async def event_message(self, message):
        if message.echo:
            return

        print(f"Message from {message.author.name}: {message.content}")

        # Check if the message is a command that should be handled
        # by TwitchIO decorators
        if message.content.startswith(TWITCH_PREFIX):
            command_name = message.content[len(TWITCH_PREFIX):].split(" ")[0]
            if command_name in ["join", "leave", "queue",
                                "available", "notavailable"]:
                # These commands will be handled by the TwitchIO command system
                # so just ensure we process them
                await self.handle_commands(message)
                return

        # Handle other commands manually
        if message.content.startswith(TWITCH_PREFIX):
            await handle_command(self, message)

        # Handle commands
        if message.content.startswith(TWITCH_PREFIX):
            await handle_command(self, message)

        # Handle AI command
        if message.content.startswith(f"{TWITCH_PREFIX}ai "):
            await handle_ai_command(self, message)
            return

        # Ensure this is always called to process commands
        # like ?join, ?leave, etc.
        await self.handle_commands(message)

    @commands.command(name="?join")
    async def join_queue(self, ctx):
        response = self.queue_manager.join_queue(ctx.author.name)
        await ctx.send(response)

    @commands.command(name="?leave")
    async def leave_queue(self, ctx):
        response = self.queue_manager.leave_queue(ctx.author.name)
        await ctx.send(response)

    @commands.command(name="?queue")
    async def show_queue(self, ctx):
        response = self.queue_manager.show_queue()
        await ctx.send(response)

    @commands.command(name="?available")
    async def make_available(self, ctx):
        response = self.queue_manager.make_available(ctx.author.name)
        await ctx.send(response)

    @commands.command(name="?notavailable")
    async def make_not_available(self, ctx):
        response = self.queue_manager.make_not_available(ctx.author.name)
        await ctx.send(response)


if __name__ == "__main__":
    bot = MurphyAI()
    bot.run()
