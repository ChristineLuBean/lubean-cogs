import discord
from redbot.core import commands

class Welcome(commands.Cog):
    """Greets new members with Hubert's specific welcome protocol."""

    def __init__(self, bot):
        self.bot = bot
        # PASTE YOUR CHANNEL ID HERE
        self.welcome_channel_id = 1472163919517847552
        # Storing your chosen quote in a variable for cleanliness
        self.welcome_msg = (
            "Hmph. Another one, {user}?\n"
            "You have entered the Gilled Glitch, SheHaxalotl's private domain. "
            "I shall be observing your progress through this sanctuary closely.\n\n"
            "To ensure you do not become a... nuisance, complete these protocols:\n\n"
            "- **The Charter:** Study #rules. We value privacy and 'Blue Team' ethics; "
            "deviations will not be tolerated.\n"
            "- **Introductions:** State your business in #introductions. What are you coding or "
            "crafting in these shallows?\n\n"
            "Whether you seek code, art, or gaming, see that you enjoy the current. "
            "Her Majesty is watching."
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Find the specific channel by ID
        channel = self.bot.get_channel(self.welcome_channel_id)
        
        if channel and channel.permissions_for(member.guild.me).send_messages:
            await channel.send(self.welcome_msg.format(user=member.mention))