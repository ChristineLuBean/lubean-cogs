from .engagement_ledger import EngagementLedger


async def setup(bot):
    await bot.add_cog(EngagementLedger(bot))