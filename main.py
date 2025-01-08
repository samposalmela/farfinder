import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents, websocket_timeout=60)

# Async function to load extensions
async def load_extensions():
    try:
        await bot.load_extension("commands.character")
        await bot.load_extension("commands.inventory")
        await bot.load_extension("commands.status")
        await bot.load_extension("commands.ship")
    except Exception as e:
        print(f"Error loading extensions: {e}")

# Event triggered when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")

# Main async function
async def main():
    try:
        await load_extensions()
        await bot.start(TOKEN)
    except asyncio.CancelledError:
        print("WebSocket connection was cancelled.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
