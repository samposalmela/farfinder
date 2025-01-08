import discord
from discord.ext import commands
from utils.data_utils import load_data, save_data
from utils.role_utils import manage_status_roles

class StatusCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def idle(self, ctx):
        user_id = str(ctx.author.id)
        data = load_data(user_id)
        active_character = data.get("active_character")

        if active_character:
            data["characters"][active_character]["status"] = "Idle"
            save_data(user_id, data)
            await manage_status_roles(ctx, "Idle")
        else:
            await ctx.send("You don't have an active character. Please switch to one first.")

    @commands.command()
    async def rest(self, ctx):
        user_id = str(ctx.author.id)
        data = load_data(user_id)
        active_character = data.get("active_character")

        if active_character:
            inventory = data["characters"][active_character]["inventory"]
            if inventory.get("rations", 0) >= 1:
                inventory["rations"] -= 1
                data["characters"][active_character]["status"] = "Resting"
                save_data(user_id, data)
                await manage_status_roles(ctx, "Resting")
                await ctx.send(f"{active_character} is now resting. A ration was consumed.")
            else:
                await ctx.send(f"{active_character} does not have enough rations to rest.")
        else:
            await ctx.send("You don't have an active character. Please switch to one first.")

    @commands.command()
    async def explore(self, ctx):
        user_id = str(ctx.author.id)
        data = load_data(user_id)
        active_character = data.get("active_character")

        if active_character:
            data["characters"][active_character]["status"] = "Exploring"
            save_data(user_id, data)
            await manage_status_roles(ctx, "Exploring")
        else:
            await ctx.send("You don't have an active character. Please switch to one first.")

async def setup(bot):
    await bot.add_cog(StatusCommands(bot))