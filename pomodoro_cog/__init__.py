from .pomodoro import Pomodoro


async def setup(bot):
    await bot.add_cog(Pomodoro(bot))