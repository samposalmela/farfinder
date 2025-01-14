import discord
from discord.ext import commands
from utils.data_utils import load_ship_inventory, save_ship_inventory, load_data, save_data, load_shop_inventory, save_shop_inventory

class FarfinderCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def farfinder(self, ctx):
        """
        Main command group for Farfinder-related operations.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid Farfinder command! Use `inventory`, `resources`, or `shop`.")

    @farfinder.group()
    async def inventory(self, ctx):
        """
        Subcommand group for inventory-related operations.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid inventory command! Use `take`, `deposit`, or `view`.")

    @inventory.command()
    async def deposit(self, ctx, material, amount: int):
        """
        Deposits materials into the Farfinder inventory.
        """
        farfinder_inventory = load_ship_inventory()

        if material not in farfinder_inventory:
            await ctx.send("Invalid material! You can deposit 'rations' or 'material'.")
            return

        # Update Farfinder inventory
        farfinder_inventory[material] += amount
        save_ship_inventory(farfinder_inventory)

        # Update character inventory
        user_id = str(ctx.author.id)
        data = load_data(user_id)
        active_character = data.get("active_character")

        if active_character:
            character_inventory = data["characters"][active_character].get("inventory", {})
            character_inventory[material] = character_inventory.get(material, 0) + amount
            data["characters"][active_character]["inventory"] = character_inventory
            save_data(user_id, data)

        await ctx.send(f"Deposited {amount} {material} to the Farfinder's inventory.")

    @inventory.command()
    async def take(self, ctx, material, amount: int):
        """
        Takes materials from the Farfinder inventory.
        """
        farfinder_inventory = load_ship_inventory()

        if material not in farfinder_inventory:
            await ctx.send("Invalid material! You can take 'rations' or 'material'.")
            return

        if farfinder_inventory[material] >= amount:
            farfinder_inventory[material] -= amount

            user_id = str(ctx.author.id)
            data = load_data(user_id)
            active_character = data.get("active_character")

            if active_character:
                character_inventory = data["characters"][active_character].get("inventory", {})
                character_inventory[material] = character_inventory.get(material, 0) + amount
                data["characters"][active_character]["inventory"] = character_inventory
                save_data(user_id, data)

            save_ship_inventory(farfinder_inventory)
            await ctx.send(f"Took {amount} {material} from the Farfinder's inventory.")
        else:
            await ctx.send(f"Not enough {material} in the Farfinder's inventory.")

    @inventory.command()
    async def view(self, ctx):
        """
        Views the current Farfinder inventory.
        """
        farfinder_inventory = load_ship_inventory()
        inventory_str = "\n".join([f"{item.capitalize()}: {quantity}" for item, quantity in farfinder_inventory.items()])
        response = f"**Farfinder Inventory:**\n{inventory_str if inventory_str else 'The inventory is empty.'}"
        await ctx.send(response)

    @farfinder.group()
    async def shop(self, ctx):
        """
        Subcommand group for shop-related operations.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid shop command! Use `view` or `buy`.")

    @shop.command()
    async def view(self, ctx):
        """
        Displays the available items in the shop with item numbers.
        """
        shop_inventory = load_shop_inventory()

        if not shop_inventory:
            await ctx.send("The shop is currently empty.")
            return

        shop_str = "\n".join([
            f"{index + 1}. {item['name'].capitalize()}: {item['price_in_tokens']} tokens (x{item['quantity']})"
            for index, item in enumerate(shop_inventory)
        ])
        response = f"**Farfinder Shop:**\n{shop_str}"
        await ctx.send(response)


    @shop.command()
    async def buy(self, ctx, item_number: int, quantity: int):
        """
        Buys items from the shop using tokens.
        """
        shop_inventory = load_shop_inventory()
        user_id = str(ctx.author.id)
        data = load_data(user_id)
        active_character = data.get("active_character")

        if not active_character:
            await ctx.send("You need an active character to buy items.")
            return

        character_inventory = data["characters"][active_character].get("inventory", {})
        tokens = character_inventory.get("tokens", 0)

        # Adjust for 1-based indexing
        index = item_number - 1

        if index < 0 or index >= len(shop_inventory):
            await ctx.send(f"Invalid item number. Please use `!farfinder shop view` to see the available items.")
            return

        item = shop_inventory[index]
        total_cost = item['price_in_tokens'] * quantity

        if tokens < total_cost:
            await ctx.send(f"You don't have enough tokens to buy {quantity} {item['name']}(s).")
            return

        if item['quantity'] < quantity:
            await ctx.send(f"The shop doesn't have enough of {item['name']}. Only {item['quantity']} available.")
            return

        # Deduct tokens and update inventories
        tokens -= total_cost
        item['quantity'] -= quantity

        character_inventory['tokens'] = tokens
        character_inventory[item['name']] = character_inventory.get(item['name'], 0) + quantity

        save_shop_inventory(shop_inventory)
        data["characters"][active_character]["inventory"] = character_inventory
        save_data(user_id, data)

        await ctx.send(f"Bought {quantity} {item['name']}(s) for {total_cost} tokens.")

async def setup(bot):
    await bot.add_cog(FarfinderCommands(bot))
