import discord
import random
from redbot.core import commands

class CritQuote(commands.Cog):
    """Hubert von Vestra Critical Hit Quotes"""

    def __init__(self, bot):
        self.bot = bot
        self.quotes = [
            "Bwahahahahahaha!",
            "Watch how weak you are!",
            "I have no need of you!",
            "Just a bug to squash!",
            "Prepare to die!",
            "We will burn together!",
            "Bow before Her Majesty!",
            "There will be no mercy!"
        ]

    @commands.command()
    async def crit(self, ctx):
        """Receive a random Hubert critical hit quote."""
        quote = random.choice(self.quotes)
        await ctx.send(f"**Hubert:** {quote}")