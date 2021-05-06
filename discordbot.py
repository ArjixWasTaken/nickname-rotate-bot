from discord.ext import tasks, commands
import discord
import json
import os
import asyncio
import math
import re
import time
import datetime as dt
import operator
import string


def format_title_case(text): return ' '.join(['(Dub)' if word.lower() == 'dub' else (
    'I' * len(word) if word.lower().replace('i', '') == '' else string.capwords(word)) for word in text.split()])


if not os.path.isfile('recommendations.json'):
    with open('recommendations.json', 'w') as f:
        json.dump([], f)


def get_recs():
    with open('recommendations.json', 'r') as f:
        return json.load(f)


def add_recommend(data):
    all_recs = get_recs()
    all_recs.append(data)
    with open('recommendations.json', 'w') as f:
        json.dump(all_recs, f, indent=4)


def update_rec(title, new_data):
    all_recs = get_recs()
    new_list = []
    found = False

    for rec in all_recs:
        if rec['title'].strip().lower() == title.strip().lower():
            new_list.append(new_data)
            found = True
            continue
        new_list.append(rec)

    with open('recommendations.json', 'w') as f:
        json.dump(new_list, f, indent=4)

    return found


def remove_rec(title):
    all_recs = get_recs()
    new_list = []
    found = False

    for rec in all_recs:
        if rec['title'].strip().lower() == title.strip().lower():
            found = True
            continue
        new_list.append(rec)

    with open('recommendations.json', 'w') as f:
        json.dump(new_list, f, indent=4)

    return found


def increment_counter_for_site(sitename, userID):
    all_recs = get_recs()
    new_array = []
    status = True

    for rec in all_recs:
        if rec['site'] == sitename:
            dat = rec
            if str(userID) in dat['voters']:
                new_array.append(dat)
                status = False
                continue
            dat['count'] += 1
            dat['voters'].append(str(userID))
            new_array.append(dat)
            continue
        new_array.append(rec)

    with open('recommendations.json', 'w') as f:
        json.dump(new_array, f, indent=4)
    return status


def get_rec(title):
    all_recs = get_recs()
    for rec in all_recs:
        if title.strip().lower() == rec['title']:
            return rec
    return False


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
    client.run(BOT_TOKEN, bot=False)


client = commands.Bot(command_prefix=command_prefix, self_bot=True, fetch_offline_members=False)
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

        if current - start >= 21550:
            raise KeyboardInterrupt


@client.event
async def on_message(message):
    messages = await message.channel.history(limit=1).flatten()
    message = messages[0]

    if message.content.startswith(f'{command_prefix}help'):
        await help(message.channel)
    elif message.content == f'{command_prefix}ping':
        await ping(message.channel)
    elif re.search(f'{command_prefix}(rec|recommend)', message.content):
        await recommend(message, re.sub(f"^{command_prefix}rec(ommend)?", "", message.content))
    elif re.search(f'{command_prefix}(lr|list-recommendations)', message.content):
        page = 1
        page_match = re.search(f'{command_prefix}(lr|list-recommendations)\s+(\d+)', message.content)

        if page_match:
            page = int(page_match.group(2))

        await list_recommendations(message.channel, pageNum=page)

"""
=========================================
    Commands
=========================================
"""
commands_ = [
    [f'{command_prefix}lr/{command_prefix}list-recommendations',
        'Short for list-recommendations, as the name suggests, it lists the recommendations from the recommendations list.'],
    [f'{command_prefix}rec/{command_prefix}recommend', 'Helps you request a source to be added in Taiyaki.'],
    [f'{command_prefix}ping', 'Sends the latency of the bot.']
]

async def help(ctx):
    embed = discord.Embed(color=0x808080)
    embed.set_author(name='Help')
    for a in commands_:
        embed.add_field(inline=False, name=a[0], value=a[1])
    embed.add_field(inline=False, name=f'{command_prefix}help',
                    value='Lists all the available commands the bot offers.')
    await ctx.send(embed=embed)

async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

#@client.command(aliases=['rec'])
async def recommend(ctx, arguments=''):
    recommended_by = str(ctx.author.id)
    finds = [operator.itemgetter(0, -1)(tuple(y for y in x if y)) for x in re.findall("-{1,2}([A-Za-z]+)\s+([A-Za-z]+)?('(.*?)')?(\"(.*?)\")?", arguments.lower())]
    title, comic_type = None, None

    for param, value in finds:
        if param in ['title', 'tt']:
            title = value
        elif param in ['type', 'tp']:
            comic_type = value

    if title and comic_type:
        all_recs = [[x['title'], x['recommended_by']] for x in get_recs()]
        for title_, requester in all_recs:
            if recommended_by == requester and title.lower().strip() == title_.lower().strip():
                await ctx.channel.send(embed=getErrorEmbed('You can\'t vote for your own request.'))
                return
        if title in [x for x, i in all_recs]:
            res = increment_counter_for_site(title, recommended_by)
            if res:
                await ctx.channel.send(embed=getSuccessEmbed('**{}** was already recommended, adding a vote to it instead...'.format(title)))
            else:
                await ctx.channel.send(embed=getErrorEmbed('You can\'t vote multiple times for the same comic.'))
            return
        add_recommend({
            'recommended_by': recommended_by,
            'title': title,
            'type': comic_type,
            'count': 1,
            'voters': []
        })
        await ctx.channel.send(embed=getSuccessEmbed('Successfully recommended **{}** *({})*.'.format(title, comic_type.upper())))
    else:
        await ctx.channel.send(embed=getErrorEmbed('Please send the correct arguments.\nExamples:\n\t``--title "The Beginning After the End" --type webtoon``\n\t\tor\n\t``-tt "The Beginning After the End" -tp webtoon``'))

#@client.command(aliases=['list-recommendations', 'lr'])
async def list_recommendations(ctx, pageNum: int = 1):
    recs = sorted(get_recs(), key=lambda x: x['count'])[::-1]
    pageEmbeds = {}

    total = len(recs)
    perPage = 10
    pages = math.ceil(total/perPage)
    current = 0

    for page in range(1, pages+1):
        embed = discord.Embed(color=0x808080)
        embed.set_author(name='Page {}{}⠀'.format(page, ' '*15))
        for i in range(perPage):
            if current <= total-1:
                tmpVar = recs[current]
                embed.add_field(
                    inline=False,
                    name=f"{current+1}. " + format_title_case(tmpVar['title']),
                    value='Type: {}\nRecommended by: {}{}'.format(
                        tmpVar['type'].title(
                        ), f"<@{tmpVar['recommended_by']}>",
                        '' if tmpVar['count'] == 1 else f"\nVotes: {tmpVar['count']}"
                    )
                )
            current += 1
        if page < pages:
            embed.set_footer(
                text=f'Use "{command_prefix}lr {page+1}" to go to the next page!')
        pageEmbeds[page] = embed

    if pageNum in pageEmbeds:
        await ctx.send(embed=pageEmbeds[pageNum])
    else:
        if pages == 0:
            await ctx.send(embed=getErrorEmbed('No recommendations were found.\nUse u!recommend to submit a recommendation.'))
            return
        await ctx.send(embed=getErrorEmbed('Page out of index.\nThere are a total of {} pages.'.format(pages)))

if __name__ == '__main__':
    run(client)
