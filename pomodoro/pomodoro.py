import asyncio
from redbot.core import commands

class Pomodoro(commands.Cog):
    """A disciplined timer for work and rest, overseen by your humble servant."""

    def __init__(self, bot):
        self.bot = bot
        self.active_sessions = set()

    @commands.command()
    async def pomo(self, ctx, work_min: int = 25, break_min: int = 5):
        """Commence a session of focused labor. Default: 25/5."""
        if ctx.author.id in self.active_sessions:
            return await ctx.send("You already have a session running. Focus, now.")
        
        self.active_sessions.add(ctx.author.id)
        await ctx.send(
            f"Very well. **{work_min} minutes** of uninterrupted focus begins now. "
            "Do not let your mind wander, or I may have to intervene."
        )

        # Work Phase
        await asyncio.sleep(work_min * 60)

        # We check if they are still in the set in case they used 'pomostop' during the sleep
        if ctx.author.id in self.active_sessions:
            await ctx.send(
                f"{ctx.author.mention}, your labor is sufficient for now. "
                f"You have **{break_min} minutes** for a brief respite. Use them wisely."
            )

            # Break Phase
            await asyncio.sleep(break_min * 60)

            if ctx.author.id in self.active_sessions:
                await ctx.send(
                    f"{ctx.author.mention}, your idleness has reached its limit. "
                    "Return to your duties at once."
                )
                self.active_sessions.remove(ctx.author.id)

    @commands.command()
    async def pomostop(self, ctx):
        """Cease the current session. I trust there is a valid reason?"""
        if ctx.author.id in self.active_sessions:
            self.active_sessions.remove(ctx.author.id)
            await ctx.send("The timer has been silenced. I shall assume this interruption was... unavoidable.")
        else:
            await ctx.send("You were not currently scheduled for any tasks. There is nothing to stop.")