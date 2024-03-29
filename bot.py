import random
from twitchio.ext import commands
from utils import suggest_alwase_variants, shazdm
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
        welcome_message = "Murphy2 initialized. Murphy2 is in alpha and may break anytime. See known issues here: https://github.com/IHasPeks/Murphy2/issues. use ?about for more info"
        for channel in TWITCH_INITIAL_CHANNELS:
            await self.get_channel(channel).send(welcome_message)

    async def event_message(self, message):
        if message.echo:
            return
        print(f"Message from {message.author.name}: {message.content}")
        await self.handle_commands(message)
        if message.content.startswith(TWITCH_PREFIX):
            command_name = message.content[len(TWITCH_PREFIX) :].split(" ")[0]
            await handle_command(self, message)
            if message.content.startswith(f"{TWITCH_PREFIX}ai "):
                await handle_ai_command(self, message)
                return
        await self.suggest_variants(message)

    async def suggest_variants(self, message):
        for suggest_func in [suggest_alwase_variants, shazdm]:
            suggestions = suggest_func(message.content)
            if suggestions:
                await message.channel.send(random.choice(suggestions))

    @commands.command(name="teamsize")
    async def set_team_size(self, ctx, size: int):
        if (
            not ctx.author.is_mod
            and ctx.author.name.lower() != ctx.channel.name.lower()
        ):
            await ctx.send("Sorry, this command is restricted to moderators only.")
            return
        if size < 1:
            await ctx.send("Team size must be at least 1.")
            return
        await ctx.send(self.queue_manager.set_team_size(size))

    @commands.command(name="join")
    async def join_queue(self, ctx):
        await ctx.send(self.queue_manager.join_queue(ctx.author.name))

    @commands.command(name="leave")
    async def leave_queue(self, ctx):
        await ctx.send(self.queue_manager.leave_queue(ctx.author.name))

    @commands.command(name="fleave")
    async def force_kick_user(self, ctx, username: str):
        if not ctx.author.is_mod:
            await ctx.send("Sorry, this command is restricted to moderators only.")
            return
        await ctx.send(self.queue_manager.force_kick(username))

    @commands.command(name="fjoin")
    async def force_join_user(self, ctx, username: str):
        if not ctx.author.is_mod:
            await ctx.send("Sorry, this command is restricted to moderators only.")
            return
        await ctx.send(self.queue_manager.force_join(username))

    @commands.command(name="moveup")
    async def move_user_up_command(self, ctx, username: str):
        if not ctx.author.is_mod:
            await ctx.send("Sorry, this command is restricted to moderators only.")
            return
        await ctx.send(self.queue_manager.move_user_up(username))

    @commands.command(name="movedown")
    async def move_user_down_command(self, ctx, username: str):
        if not ctx.author.is_mod:
            await ctx.send("Sorry, this command is restricted to moderators only.")
            return
        await ctx.send(self.queue_manager.move_user_down(username))

    @commands.command(name="Q")
    async def show_queue(self, ctx):
        main_queue_msg, overflow_queue_msg = self.queue_manager.show_queue()
        await ctx.send(main_queue_msg)
        # Check if the overflow queue message is not just the default empty message before sending
        if overflow_queue_msg != "Overflow Queue is empty.":
            await ctx.send(overflow_queue_msg)

    @commands.command(name="here")
    async def make_available(self, ctx):
        await ctx.send(self.queue_manager.make_available(ctx.author.name))

    @commands.command(name="nothere")
    async def make_not_available(self, ctx):
        await ctx.send(self.queue_manager.make_not_available(ctx.author.name))

    @commands.command(name="shuffle")
    async def shuffle_queue(self, ctx):
        if not ctx.author.is_mod:
            await ctx.send("Sorry, this command is restricted to moderators only.")
            return
        response = self.queue_manager.shuffle_teams()
        if "\n" in response:
            team1_response, team2_response = response.split("\n")
            await ctx.send(team1_response)
            await ctx.send(team2_response)
        else:
            await ctx.send(response)


if __name__ == "__main__":
    bot = MurphyAI()
    bot.run()
