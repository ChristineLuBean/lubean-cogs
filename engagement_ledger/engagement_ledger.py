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
        self.config.register_guild(log_channel=None)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # Trigger: :coin: emoji (🪙)
        if str(payload.emoji) != "🪙":
            return

        # Security Gate: Only Christine (SheHaxalotl)
        if payload.user_id != 242836394488233995:
            return

        if not payload.guild_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        
        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return

        # Prevent awarding bots or self
        if message.author.bot or message.author.id == payload.user_id:
            return

        # Update points
        async with self.config.user(message.author).all() as user_data:
            user_data["points"] += 1
            new_total = user_data["points"]

        # Log to #mod-logs
        log_id = await self.config.guild(guild).log_channel()
        if log_id:
            log_chan = guild.get_channel(log_id)
            if log_chan:
                embed = discord.Embed(
                    title="[System Log] Currency Minted",
                    description=f"**Target:** {message.author.mention}\n**New Balance:** {new_total} 🪙",
                    color=0x2ecc71 # Terminal Green
                )
                embed.set_footer(text=f"Authorized by SheHaxalotl | ID: {message.author.id}")
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

async def setup(bot):
    await bot.add_cog(EngagementLedger(bot))