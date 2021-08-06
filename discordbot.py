from discord.ext import tasks, commands
import discord
import json
import os
import asyncio
import time

if not os.path.isfile('settings.json'):
    with open('settings.json', 'w') as f:
        json.dump({
            "servers": {}
        }, f)


def get_settings():
    with open('settings.json', 'r') as f:
        return json.load(f)


def add_user(guild_id, userID, member):
    settings = get_settings()

    if str(guild_id) not in settings["servers"]:
        settings["servers"][str(guild_id)] = {}
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)

    if str(userID) not in settings['servers'][str(guild_id)]:
        settings['servers'][str(guild_id)][str(userID)] = (member.nick if member.nick else member.name) + " "

        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    return False


def remove_user(guild_id, userID):
    settings = get_settings()
    if str(guild_id) not in settings['servers']:
        settings['servers'][str(guild_id)] = {}

    del settings['servers'][str(guild_id)][str(userID)]

    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)


def getSuccessEmbed(Msg):
    embed = discord.Embed(color=0x00ff00)
    embed.set_author(name='Success')
    embed.description = Msg
    return embed


def getErrorEmbed(errMsg):
    embed = discord.Embed(color=0xFF0000)
    embed.set_author(name='Error')
    embed.description = errMsg
    return embed


"""
=========================================
    Setup
=========================================
"""
command_prefix = '!'
BOT_TOKEN = os.environ['TOKEN']


def run(client):
    client.run(BOT_TOKEN, bot=True)


client = commands.Bot(command_prefix=command_prefix, fetch_offline_members=False)
client.remove_command('help')


"""
=========================================
    Events
=========================================
"""
nicknames = {}


@client.event
async def on_ready():
    print('Discord bot is ready.')
    start = time.time()

    while True:
        await asyncio.sleep(1)
        servers = get_settings()['servers']
        for server in servers:
            serv = client.get_guild(int(server))
            if server not in nicknames:
                nicknames[server] = {}

            for member in servers[server]:
                member_ = await serv.fetch_member(int(member))

                if member not in nicknames[server]:
                    nicknames[server][member] = servers[server][member]
                else:
                    nick = nicknames[server][member]
                    nicknames[server][member] = nick[1:] + nick[0]
                try:
                    await member_.edit(nick="| " + nicknames[server][member] + " |")  # noqa
                except:
                    pass

        current = time.time()

        if current - start >= 14400:
            raise KeyboardInterrupt

"""
=========================================
    Commands
=========================================
"""


@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')


@client.command(aliases=["rotate"])
async def rotate_toggle(ctx, member: discord.User = None):
    global nicknames
    if member is not None and ctx.author.id in (246755970858876930, 674710789138939916):
        if (add_user(str(ctx.message.channel.guild.id), str(member.id), member)):
            await ctx.send(embed=getSuccessEmbed("Successfully added {}.".format(member.mention)))
        else:
            remove_user(str(ctx.message.channel.guild.id), str(member.id))
            del nicknames[str(ctx.message.channel.guild.id)][str(member.id)]
            await ctx.send(embed=getSuccessEmbed("Successfully removed {}.".format(member.mention)))
    else:
        if (add_user(str(ctx.message.channel.guild.id), str(ctx.author.id), ctx.message.author)):
            await ctx.send(embed=getSuccessEmbed("Successfully added you."))
        else:
            remove_user(str(ctx.message.channel.guild.id), str(ctx.author.id))
            del nicknames[str(ctx.message.channel.guild.id)][str(ctx.author.id)]
            await ctx.send(embed=getSuccessEmbed("Successfully removed you."))


@client.command()
async def exit(ctx):
    if ctx.author.id in (246755970858876930, 674710789138939916):
        await ctx.send(embed=getSuccessEmbed("Exiting..."))
        raise KeyboardInterrupt

if __name__ == '__main__':
    run(client)
