from discord.ext import tasks, commands
import discord
import json
import os
import asyncio
import time

if not os.path.isfile('settings.json'):
    with open('settings.json', 'w') as f:
        json.dump({
            "channels": {}
        }, f)


def get_settings():
    with open('settings.json', 'r') as f:
        return json.load(f)


def add_user(channelID, userID):
    settings = get_settings()
    if str(channelID) not in settings['channels']:
        settings['channels'][str(channelID)] = []

    if str(userID) not in settings['channels'][str(channelID)]:
        settings['channels'][str(channelID)].append(str(userID))

        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)


def remove_user(channelID, userID):
    settings = get_settings()
    if str(channelID) not in settings['channels']:
        settings['channels'][str(channelID)] = []

    settings['channels'][str(channelID)].remove(str(userID))

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


@client.event
async def on_ready():
    print('Discord bot is ready.')
    start = time.time()
    current = start

    while True:
        await asyncio.sleep(1)
        current += 1

        if current - start >= 17959:
            raise KeyboardInterrupt

"""
=========================================
    Commands
=========================================
"""


@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')


@client.command()
async def rotate_me(ctx, arguments=''):
    pass


if __name__ == '__main__':
    run(client)
