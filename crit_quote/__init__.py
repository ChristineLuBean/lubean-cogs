from .crit_quote import CritQuote

async def setup(bot):
  await bot.add_cog(CritQuote(bot))