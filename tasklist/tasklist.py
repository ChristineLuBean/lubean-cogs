import discord
from redbot.core import commands, Config

class Tasklist(commands.Cog):
    """A simple cog to manage your personal task list."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890) # Use a unique ID
        
        # Default settings for each user
        default_user = {
            "tasks": []
        }
        self.config.register_user(**default_user)

    @commands.group()
    async def task(self, ctx):
        """Task list management commands."""
        pass

    @task.command(name="add")
    async def task_add(self, ctx, *, description: str):
        """Add a task to your list."""
        async with self.config.user(ctx.author).tasks() as tasks:
            tasks.append(description)
        await ctx.send(f"✅ Added: {description}")

    @task.command(name="list")
    async def task_list(self, ctx):
        """View your current tasks."""
        tasks = await self.config.user(ctx.author).tasks()
        if not tasks:
            return await ctx.send("Your task list is empty!")

        list_text = "\n".join([f"{i+1}. {task}" for i, task in enumerate(tasks)])
        embed = discord.Embed(title=f"{ctx.author.display_name}'s Tasks", 
                              description=list_text, 
                              color=discord.Color.blue())
        await ctx.send(embed=embed)

    @task.command(name="done")
    async def task_done(self, ctx, index: int):
        """Remove a task by its number."""
        async with self.config.user(ctx.author).tasks() as tasks:
            if 0 < index <= len(tasks):
                removed = tasks.pop(index - 1)
                await ctx.send(f"🗑️ Removed: {removed}")
            else:
                await ctx.send("Invalid task number.")  