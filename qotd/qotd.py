import discord
import datetime
from discord.ext import tasks
from redbot.core import commands, Config

class QOTD(commands.Cog):
    """A Question of the Day cog for scheduled posting."""

    def __init__(self, bot):
        self.bot = bot
        # Unique identifier for your cog's data
        self.config = Config.get_conf(self, identifier=8273641526)
        
        # Default settings for every server the bot is in
        default_guild = {
            "questions": [],
            "channel_id": None,
            "posted_today": None  # Tracks the last date a question was posted
        }
        self.config.register_guild(**default_guild)
        
        # Start the background task
        self.qotd_check.start()

    def cog_unload(self):
        # Stop the task if the cog is unloaded
        self.qotd_check.cancel()

    @commands.admin_or_permissions(manage_guild=True)
    @commands.command()
    async def qotdchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel where the Question of the Day will be posted."""
        await self.config.guild(ctx.guild).channel_id.set(channel.id)
        await ctx.send(f"✅ QOTD channel has been set to {channel.mention}")

    @commands.command()
    async def schedule_q(self, ctx, date: str, *, question: str):
        """
        Schedule a question. 
        Format: [p]schedule_q YYYY-MM-DD Your question here
        Example: [p]schedule_q 2026-04-14 What is your favorite dessert?
        """
        try:
            # Validate the date format
            datetime.date.fromisoformat(date)
        except ValueError:
            return await ctx.send("❌ Invalid date format. Please use **YYYY-MM-DD**.")

        async with self.config.guild(ctx.guild).questions() as questions:
            questions.append({"text": question, "date": date})
        
        await ctx.send(f"📅 Scheduled for **{date}**: {question}")

    @commands.command()
    async def qlist(self, ctx):
        """View the queue of upcoming questions."""
        questions = await self.config.guild(ctx.guild).questions()
        if not questions:
            return await ctx.send("The queue is currently empty.")

        msg = "**Upcoming Questions:**\n"
        # Sort questions by date before displaying
        sorted_qs = sorted(questions, key=lambda x: x['date'])
        for i, q in enumerate(sorted_qs, 1):
            msg += f"{i}. `{q['date']}`: {q['text']}\n"
        
        await ctx.send(msg)

    @tasks.loop(minutes=30)
    async def qotd_check(self):
        """Check every 30 minutes if there is a question to post for today."""
        today = datetime.date.today().isoformat()
        all_guilds = await self.config.all_guilds()

        for guild_id, data in all_guilds.items():
            # Basic checks: Is the guild/channel valid? Has it already posted today?
            guild = self.bot.get_guild(guild_id)
            if not guild or not data["channel_id"] or data["posted_today"] == today:
                continue

            channel = guild.get_channel(data["channel_id"])
            if not channel:
                continue

            to_post = None
            remaining_questions = []

            # Find a question that matches today's date
            for q in data["questions"]:
                if q["date"] == today and not to_post:
                    to_post = q["text"]
                else:
                    remaining_questions.append(q)

            if to_post:
                # Create the visual embed
                embed = discord.Embed(
                    title="❓ Question of the Day",
                    description=to_post,
                    color=discord.Color.blue(),
                    timestamp=datetime.datetime.now()
                )
                
                try:
                    await channel.send(embed=embed)
                    # Update storage: remove the posted question and set the posted date
                    await self.config.guild(guild).questions.set(remaining_questions)
                    await self.config.guild(guild).posted_today.set(today)
                except discord.Forbidden:
                    # Log if the bot doesn't have permission to post in that channel
                    continue

    @qotd_check.before_loop
    async def before_qotd_check(self):
        # Wait for the bot to fully connect before starting the loop
        await self.bot.wait_until_ready()