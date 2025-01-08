import discord

async def manage_status_roles(ctx, new_status):
    member = ctx.author
    guild = ctx.guild

    # Define the status roles
    status_roles = ["Idle", "Resting", "Exploring"]
    role_to_assign = discord.utils.get(guild.roles, name=new_status)

    if not role_to_assign:
        await ctx.send(f"Role '{new_status}' not found. Please create it.")
        return

    # Remove other status roles
    for role_name in status_roles:
        role = discord.utils.get(guild.roles, name=role_name)
        if role and role in member.roles:
            await member.remove_roles(role)

    # Assign the new role
    await member.add_roles(role_to_assign)
    await ctx.send(f"{new_status} role assigned successfully!")
