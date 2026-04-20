import discord
from redbot.core import commands, Config
import operator

class EngagementLedger(commands.Cog):
    """Modular point tracking for the SheHaxalotl community."""

    def __init__(self, bot):
        self.bot = bot
        # Identifier is a unique int, using your bday + project year
        self.config = Config.get_conf(self, identifier=19892026, force_registration=True)
        self.config.register_user(points=0)
        self.config.register_guild(log_channel=None, watch_channel=None)

    @commands.command()
    async def award(self, ctx, amount: int = 1):
        """
        Award points to the author of the message you are replying to.
        Usage: (as a reply) !award 5
        """
        # Security: Only you (Christine) can mint currency
        if ctx.author.id != 242836394488233995:
            return

        # Check if the command is a reply
        if not ctx.message.reference:
            return await ctx.send("⚠️ You must reply to a message to award points.")

        # Fetch the replied-to message
        replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        target_user = replied_message.author

        # Prevent awarding bots or yourself
        if target_user.bot:
            return await ctx.send("⚠️ Even the finest automatons do not require coin.")
        if target_user.id == ctx.author.id:
            return await ctx.send("⚠️ Self-rewarding is not permitted in this ledger.")

        # Update the points
        async with self.config.user(target_user).all() as user_data:
            user_data["points"] += amount
            new_total = user_data["points"]

        # Confirmation and Log
        await ctx.tick() # Adds a checkmark reaction to your command
        
        log_id = await self.config.guild(ctx.guild).log_channel()
        if log_id:
            log_chan = ctx.guild.get_channel(log_id)
            if log_chan:
                embed = discord.Embed(
                    title="[System Log] Manual Minting",
                    description=(
                        f"**Authorized by:** {ctx.author.mention}\n"
                        f"**Recipient:** {target_user.mention}\n"
                        f"**Amount:** {amount} 🪙\n"
                        f"**New Balance:** {new_total} 🪙"
                    ),
                    color=0x2ecc71
                )
                await log_chan.send(embed=embed)

    @commands.command()
    async def wallet(self, ctx):
        """Check your current coin balance."""
        pts = await self.config.user(ctx.author).points()
        await ctx.send(f"🛡️ **[Wallet Status]** {ctx.author.name}, you have **{pts}** 🪙 in your ledger.")

    @commands.command(aliases=["topglitches"])
    async def leaderboard(self, ctx):
        """View the top contributors in the system."""
        all_users = await self.config.all_users()
        if not all_users:
            return await ctx.send("The ledger is currently empty.")

        # Sort by points descending
        sorted_users = sorted(all_users.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        
        description = ""
        for i, (user_id, data) in enumerate(sorted_users, 1):
            user = self.bot.get_user(user_id)
            user_name = user.name if user else f"User_{user_id}"
            description += f"{i}. **{user_name}** — {data['points']} 🪙\n"

        embed = discord.Embed(
            title="📂 [System Directory] Top Tacticians",
            description=description,
            color=0x2ecc71
        )
        await ctx.send(embed=embed)

    @commands.group()
    @commands.admin_or_permissions(manage_guild=True)
    async def ledgerset(self, ctx):
        """Configure the Engagement Ledger."""
        pass

    @ledgerset.command()
    async def logchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel for point audit logs."""
        await self.config.guild(ctx.guild).log_channel.set(channel.id)
        await ctx.send(f"Audit logs set to {channel.mention}.")

    @ledgerset.command()
    async def watchchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel to watch for coin reactions."""
        await self.config.guild(ctx.guild).watch_channel.set(channel.id)
        await ctx.send(f"Now watching {channel.mention} for 🪙 reactions.")

async def setup(bot):
    await bot.add_cog(EngagementLedger(bot))