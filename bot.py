import random
from twitchio.ext import commands
from utils import suggest_alwase_variants
from utils import shazdm
from commands import handle_command
from scheduler import start_scheduler
from queue_manager import QueueManager
from ai_command import handle_ai_command
from config import (
    TWITCH_TOKEN,
    TWITCH_CLIENT_ID,
    TWITCH_PREFIX,
    MOD_PREFIX,
    TWITCH_INITIAL_CHANNELS,
)


class MurphyAI(commands.Bot):

    def __init__(self):
        super().__init__(
            token=TWITCH_TOKEN,
            client_id=TWITCH_CLIENT_ID,
            prefix=TWITCH_PREFIX,
            mod_prefix=MOD_PREFIX,
            initial_channels=TWITCH_INITIAL_CHANNELS,
        )
        self.queue_manager = QueueManager()

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"ID | {self.user_id}")
        await start_scheduler(self)
        self.queue_manager.start_cleanup_task(self.loop)
        # Send a message in chat when the bot is started
        for channel in TWITCH_INITIAL_CHANNELS:
            await self.get_channel(channel).send(
                "Murphy2 initialized. Murphy2 is in alpha and may break at anytime. See known issues here: https://github.com/IHasPeks/Murphy2/issues. use ?about for more information"
            )

    async def event_message(self, message):
        if message.echo:
            return

        print(f"Message from {message.author.name}: {message.content}")

        # Process commands with TwitchIO command system and custom handlers
        await self.handle_commands(message)
        if message.content.startswith(TWITCH_PREFIX):
            command_name = message.content[len(TWITCH_PREFIX) :].split(" ")[0]
            # If the command is not recognized by TwitchIO, it might be a custom command
            if command_name not in [
                "join",
                "leave",
                "queue",
                "available",
                "notavailable",
            ]:

                # Handle commands
                if message.content.startswith(TWITCH_PREFIX):
                    await handle_command(self, message)

                # Handle AI command
                if message.content.startswith(f"{TWITCH_PREFIX}ai "):
                    await handle_ai_command(self, message)
                    return

        # Check for 'always' in message and suggest 'alwase' variants
        alwase_suggestions = suggest_alwase_variants(message.content)
        if alwase_suggestions:
            suggestion = random.choice(alwase_suggestions)
            await message.channel.send(suggestion)

        dms_suggestions = shazdm(message.content)
        if dms_suggestions:
            dms_suggestion = random.choice(dms_suggestions)
            await message.channel.send(dms_suggestion)

    @commands.command(name="join")
    async def join_queue(self, ctx):
        response = self.queue_manager.join_queue(ctx.author.name)
        await ctx.send(response)

    @commands.command(name="leave")
    async def leave_queue(self, ctx):
        response = self.queue_manager.leave_queue(ctx.author.name)
        await ctx.send(response)

    @commands.command(name="queue")
    async def show_queue(self, ctx):
        response = self.queue_manager.show_queue()
        await ctx.send(response)

    @commands.command(name="here")
    async def make_available(self, ctx):
        response = self.queue_manager.make_available(ctx.author.name)
        await ctx.send(response)

    @commands.command(name="nothere")
    async def make_not_available(self, ctx):
        response = self.queue_manager.make_not_available(ctx.author.name)
        await ctx.send(response)
    
    @commands.command(name="shuffle")
    async def shuffle_queue(self, ctx):
        response = self.queue_manager.shuffle_teams()
        # Split the response into two parts based on the newline character
        team1_response, team2_response = response.split('\n')
        # Send each part as a separate message
        await ctx.send(team1_response)
        await ctx.send(team2_response)

if __name__ == "__main__":
    bot = MurphyAI()
    bot.run()
