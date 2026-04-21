from .tasklist import Tasklist

async def setup(bot):
    await bot.add_cog(Tasklist(bot))