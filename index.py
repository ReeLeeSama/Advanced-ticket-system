import asyncio
import os
import os.path
import discord
import json
from discord import permissions
from discord.ext import commands

client=commands.Bot(command_prefix='>')


@client.event
async def on_ready():
    print("Bot is online")

@client.command()
async def ping(ctx):
    await ctx.reply("Pong")

@client.command()
@commands.has_permission(administrator=True)
async def setup(ctx,channel:discord.TextChannel):
        g_id = ctx.guild.id
        c_id = channel.id
        category = await ctx.guild.create_category("Tickets")
        ctg_id = category.id
        done_chan = await category.create_text_channel(f"ticket-{ctx.author.name}",topic="Tickets have been configured",permission_synced=True)
        await done_chan.set_permissions(ctx.author, read_messages=True, send_messages=True)
        await done_chan.send(f"{ctx.author.mention} this is a ticket to confirm that the configuration is working. Do not delete this category. To close the ticket run the ``>close`` command")
        embed=discord.Embed(title=f"{ctx.guild.name} Tickets",description="React to this message to make a ticket",color=discord.Colour.blurple())
        sen = await channel.send(embed=embed)
        m_id = sen.id
        await sen.add_reaction("🎫")
        with open('config.json','r') as f:
            config = json.load(f)
        config[str(g_id)] = {}
        config[str(g_id)]['channel'] = c_id
        config[str(g_id)]['category'] = ctg_id
        config[str(g_id)]['message'] = m_id
        with open('config.json','w') as f:
                json.dump(config, f)
        await ctx.reply("Done.")
        
@client.command()
async def configuration(ctx):
    g_id = ctx.guild.id
    with open('config.json','r') as f:
        e = json.load(f)
    channel = client.get_channel(e[str(g_id)]['channel'])
    await ctx.reply(f"{channel.mention}")

@client.command()
async def close(ctx):
    if ctx.channel.name.startswith('ticket-'):
        await ctx.reply("Deleting in 5 seconds")
        await asyncio.sleep(5)
        await ctx.channel.delete()
    else:
        await ctx.reply("This commands works for tickets only.")

@client.event
async def on_raw_reaction_add(payload):
    g_id = payload.guild_id
    with open('config.json','r') as f:
        config = json.load(f)
    c_id = config[str(g_id)]['channel']
    m_id = config[str(g_id)]['message']
    ctg_id = config[str(g_id)]['category']
    channel = client.get_channel(config[str(g_id)]['channel'])
    if payload.member.id != client.user.id and str(payload.emoji) == u"\U0001F3AB":
    
        if payload.message_id == m_id:
            guild = client.get_guild(payload.guild_id)
            
            for category in guild.categories:
                    if category.id == ctg_id:
                        break
            ticket_channel = await category.create_text_channel(f"ticket-{payload.member.display_name}", topic=f"Ticket for {payload.member.display_name}.", permission_synced=True)
            await ticket_channel.set_permissions(payload.member, read_messages=True, send_messages=True)
            mention_member = f"{payload.member.mention}"
            message = await channel.fetch_message(m_id)
            await message.remove_reaction(payload.emoji, payload.member)

@client.event
async def on_guild_join(guild):
    if not os.path.isdir('guilds/{guild.id}'):
        os.mkdir(f"guilds/{guild.id}")
        pass
    if not os.path.isdir('guilds/{guild.id}/tickets'):
        os.mkdir(f"guilds/{guild.id}/tickets")
        pass
        

client.run("TOKEN_HERE")
