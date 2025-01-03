import discord
from discord.ext import commands

# Set up the bot with a prefix
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Event for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# A simple command
@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I'm your bot.")

# Run the bot
bot.run('YOUR_BOT_TOKEN')  # Replace with your bot's token

