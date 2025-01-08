import discord
from discord.ext import commands
from utils.data_utils import load_data, save_data

class CharacterCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to register a new character
    @commands.command()
    async def register_character(self, ctx, character_name, character_class, species, background, description=""):
        user_id = str(ctx.author.id)
        data = load_data(user_id)

        if character_name in data["characters"]:
            await ctx.send(f"Character {character_name} already registered.")
            return

        data["characters"][character_name] = {
            "class": character_class,
            "species": species,
            "background": background,
            "level": 1,
            "status": "Idle",
            "description": description,
            "inventory": {'rations': 0, 'material': 0}
        }
        save_data(user_id, data)
        await ctx.send(f"Character {character_name} registered successfully!")

    # Command to switch between characters
    @commands.command()
    async def switch_character(self, ctx, character_name):
        user_id = str(ctx.author.id)
        data = load_data(user_id)

        if character_name in data["characters"]:
            data["active_character"] = character_name
            save_data(user_id, data)
            await ctx.send(f"Switched to character {character_name}.")
        else:
            await ctx.send("Character not found. Please register the character first.")

    # Command to view the active character's profile
    @commands.command()
    async def profile(self, ctx):
        user_id = str(ctx.author.id)
        data = load_data(user_id)

        active_character = data.get("active_character")
        if active_character:
            character_info = data["characters"].get(active_character)
            profile_str = (
                f"Name: {active_character}\n"
                f"Class: {character_info['class']}\n"
                f"Species: {character_info['species']}\n"
                f"Background: {character_info['background']}\n"
                f"Level: {character_info['level']}\n"
                f"Status: {character_info['status']}\n"
                f"Description: {character_info['description'] if character_info['description'] else 'No description set.'}"
            )
            await ctx.send(profile_str)
        else:
            await ctx.send("You don't have an active character. Please switch to one first.")

    # Command to list all characters for the user
    @commands.command()
    async def my_characters(self, ctx):
        user_id = str(ctx.author.id)
        data = load_data(user_id)

        characters = data["characters"]
        character_list = [name for name in characters if name != data["active_character"]]
        await ctx.send(f"Your characters: {', '.join(character_list) if character_list else 'None'}")

    # Command to set or update attributes of the active character
    @commands.command()
    async def set(self, ctx, attribute: str, *, value: str):
        user_id = str(ctx.author.id)
        data = load_data(user_id)

        active_character = data.get("active_character")
        if not active_character:
            await ctx.send("You don't have an active character. Please switch to one first.")
            return

        # Validate the attribute
        valid_attributes = ["class", "species", "background", "level", "description"]
        if attribute not in valid_attributes:
            await ctx.send(f"Invalid attribute! You can set: {', '.join(valid_attributes)}.")
            return

        # If the attribute is 'level', ensure it's a positive integer
        if attribute == "level":
            try:
                value = int(value)
                if value <= 0:
                    raise ValueError("Level must be a positive integer.")
            except ValueError:
                await ctx.send("Level must be a positive integer.")
                return

        # Update the attribute
        data["characters"][active_character][attribute] = value
        save_data(user_id, data)

        await ctx.send(f"Updated {attribute} for {active_character} to: {value}.")

async def setup(bot):
    await bot.add_cog(CharacterCommands(bot))
