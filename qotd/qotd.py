import discord
import datetime
from discord.ext import tasks
from redbot.core import commands, Config

class QOTD(commands.Cog):
    """A Question of the Day cog for scheduled posting."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=8273641526)
        default_guild = {
            "questions": [], 
            "channel_id": None, 
            "posted_today": None,
            "current_question": None
        }
        self.config.register_guild(**default_guild)
        self.qotd_check.start()

    def cog_unload(self):
        self.qotd_check.cancel()

    @commands.group()
    async def qotd(self, ctx):
        """Manage Question of the Day settings and queue."""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="❓ QOTD Bot Guide",
                description="Use these commands to manage your daily questions.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Setup Channel", value="`!qotd channel #channel`", inline=False)
            embed.add_field(name="Schedule Question", value="`!qotd add YYYY-MM-DD <question>`", inline=False)
            embed.add_field(name="View Queue", value="`!qotd list`", inline=False)
            embed.add_field(name="Repost Current", value="`!qotd repost`", inline=False)
            embed.add_field(name="Force Post Today", value="`!qotd force`", inline=False)
            embed.set_footer(text="Format dates as Year-Month-Day (e.g., 2026-04-13)")
            await ctx.send(embed=embed)

    @qotd.command(name="force")
    @commands.admin_or_permissions(manage_guild=True)
    async def qotd_force(self, ctx):
        """Force post today's scheduled question immediately."""
        today = datetime.date.today().isoformat()
        channel_id = await self.config.guild(ctx.guild).channel_id()
        
        if not channel_id:
            return await ctx.send("❌ No QOTD channel set. Use `!qotd channel` first.")
        
        channel = ctx.guild.get_channel(channel_id)
        if not channel:
            return await ctx.send("❌ I can't find the QOTD channel. Is it deleted?")

        async with self.config.guild(ctx.guild).questions() as questions:
            to_post = None
            index_to_remove = -1
            
            for i, q in enumerate(questions):
                if q["date"] == today:
                    to_post = q["text"]
                    index_to_remove = i
                    break
            
            if to_post:
                embed = discord.Embed(title="❓ Question of the Day", description=to_post, color=discord.Color.blue())
                await channel.send(embed=embed)
                
                # Update records
                await self.config.guild(ctx.guild).current_question.set(to_post)
                await self.config.guild(ctx.guild).posted_today.set(today)
                questions.pop(index_to_remove)
                
                await ctx.send("✅ Today's question has been forced and posted.")
            else:
                await ctx.send(f"❌ No question is scheduled for today ({today}).")

    @qotd.command(name="repost")
    async def qotd_repost(self, ctx):
        """Repost the current Question of the Day."""
        current = await self.config.guild(ctx.guild).current_question()
        if not current:
            return await ctx.send("There is no active Question of the Day to repost!")

        embed = discord.Embed(title="❓ Question of the Day (Repost)", description=current, color=discord.Color.blue())
        await ctx.send(embed=embed)

    @qotd.command(name="channel")
    @commands.admin_or_permissions(manage_guild=True)
    async def qotd_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel where QOTD will be posted."""
        await self.config.guild(ctx.guild).channel_id.set(channel.id)
        await ctx.send(f"✅ QOTD channel set to {channel.mention}")

    @qotd.command(name="add")
    async def schedule_q(self, ctx, date: str, *, question: str):
        """Schedule a question: !qotd add YYYY-MM-DD <question>"""
        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            return await ctx.send("❌ Use **YYYY-MM-DD** format.")
        async with self.config.guild(ctx.guild).questions() as questions:
            questions.append({"text": question, "date": date})
        await ctx.send(f"📅 Scheduled for **{date}**.")

    @qotd.command(name="list")
    async def qlist(self, ctx):
        """View upcoming questions."""
        questions = await self.config.guild(ctx.guild).questions()
        if not questions:
            return await ctx.send("The queue is empty.")
        sorted_qs = sorted(questions, key=lambda x: x['date'])
        msg = "\n".join([f"`{q['date']}`: {q['text']}" for q in sorted_qs])
        await ctx.send(f"**Upcoming Questions:**\n{msg}")

    @tasks.loop(minutes=30)
    async def qotd_check(self):
        today = datetime.date.today().isoformat()
        all_guilds = await self.config.all_guilds()
        for guild_id, data in all_guilds.items():
            guild = self.bot.get_guild(guild_id)
            if not guild or not data["channel_id"] or data["posted_today"] == today:
                continue
            channel = guild.get_channel(data["channel_id"])
            if not channel: continue
            
            to_post = None
            remaining = []
            for q in data["questions"]:
                if q["date"] == today and not to_post:
                    to_post = q["text"]
                else:
                    remaining.append(q)
            
            if to_post:
                embed = discord.Embed(title="❓ Question of the Day", description=to_post, color=discord.Color.blue())
                await channel.send(embed=embed)
                await self.config.guild(guild).current_question.set(to_post)
                await self.config.guild(guild).questions.set(remaining)
                await self.config.guild(guild).posted_today.set(today)

    @qotd_check.before_loop
    async def before_qotd_check(self):
        await self.bot.wait_until_ready()