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