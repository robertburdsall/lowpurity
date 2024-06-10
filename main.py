# bot.py
import json
import os
import typing

import discord
from discord.ext import commands
from dotenv import load_dotenv
from googleapiclient.discovery import build
import random
from datetime import datetime, timedelta

indents = discord.Intents.all()
indents.members = True

from mee6_py_api import API

mee6API = API(932430580765839451)

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = os.getenv('OWNER_ID')
YT_API_KEY = os.getenv('YOUTUBE_API')
youtube = build("youtube", "v3", developerKey=YT_API_KEY)
AUDIT_LOGS_CHANNEL = 945749408555884608
LEVEL_UP_CHANNELS = [932549351585251338]

bot = commands.Bot(command_prefix='/', intents=indents)

invites = {}
invites_youtube = {
    'Yg8rWBzE6E': '1 Old',
    'FDaWWTZpWt': '2 Old',
    'BNFCsFWkRJ': 'Skoice v3 https://youtu.be/HF4jPrussjs'
}

levels = {}

with open('levels.json', 'r') as f:
    json_data = f.read()

levels = json.loads(json_data)
print(levels)

# string userid : [int xp, int level, int time]

level_barriers = [40]
# format the barriers for the levels
i = 1
while i < 60:
    if i == 1:
        level_barriers.append(74)
    else:
        level_barriers.append(level_barriers[i - 1] + (level_barriers[i - 1] - level_barriers[i - 2]) ** 1.0019)
    i += 1


def get_channel_stats(channel_id):
    request = youtube.channels().list(
        part='statistics',
        id=channel_id
    )
    response = request.execute()
    stats = response['items'][0]['statistics']
    return stats


def find_invite_by_code(invite_list, code):
    for invite in invite_list:
        if invite.code == code:
            return invite


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Mykyta sucks ‼️"))

    for guild in bot.guilds:
        invites[guild.id] = await guild.invites()

    print(f'logged in as {bot.user}')
    await bot.tree.sync(guild=discord.Object(id=932430580765839451))
    await bot.tree.sync()


# magic code

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(932430581374021674)
    await channel.send(f':rose: {member.mention}')
    embed = discord.Embed(title="Welcome to Highpurity's Rose Garden! :rose:",
                          description="• Read our rules at https://discord.com/channels/932430580765839451"
                                      "/932458730509979648 \n • If you need assistance, open a ticket in "
                                      "https://discord.com/channels/932430580765839451/943688886658433104 \n • Check "
                                      "out new YouTube videos in "
                                      "https://discord.com/channels/932430580765839451/932523626807320596",
                          color=0xff6961)
    embed.set_image(
        url="https://66.media.tumblr.com/d3fefcec6a466d1e66bfd4451ddc64c9/tumblr_ozbx86pCdW1w5n1g1o1_500.gif")
    await channel.send(embed=embed)

    invites_before_join = invites[member.guild.id]
    invites_after_join = await member.guild.invites()

    for invite in invites_before_join:
        if invite.uses < find_invite_by_code(invites_after_join, invite.code).uses:
            print(f"Member {member.name} Joined")
            print(f"Invite Code: {invite.code}")
            print(f"Inviter: {invite.inviter}")

    invites[member.guild.id] = invites_after_join
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f'Welcome {member}! 💕'))


@bot.event
async def on_member_remove(member):
    # Updates the cache when a user leaves to make sure
    # everything is up to date

    invites[member.guild.id] = await member.guild.invites()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f"Bye {member}! 👋"))


@bot.event
async def on_message(message):
    print(f'{message.author}: {message.content}')
    if message.author == bot.user:
        return
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f"Hello {message.author}! 💬"))

    if message.channel.id in LEVEL_UP_CHANNELS:
        # string userid : [int xp, int level, int time]
        # leveling stuff
        XP_ADDED = random.randint(5, 21)
        if str(message.author.id) not in levels.keys():
            levels[str(message.author.id)] = [XP_ADDED, 1, ]
            print(f'{message.author}: added to levels.json!')
            with open("levels.json", "w") as outfile:
                json.dump(levels, outfile)
            return

        async for msg in message.channel.history():
            if msg.author == message.author and message.id != msg.id:
                time_difference = message.created_at - msg.created_at
                if time_difference > timedelta(minutes=5):
                    print(f'{message.author}: gained {XP_ADDED} XP!')
                    NEW_XP = levels[str(message.author.id)][0] + XP_ADDED
                    if NEW_XP > level_barriers[levels[str(message.author.id)][1] + 1]:
                        levels[str(message.author.id)] = [NEW_XP, levels[str(message.author.id)] + 1]
                    else:
                        levels[str(message.author.id)] = [NEW_XP, levels[str(message.author.id)]]
                    with open("levels.json", "w") as outfile:
                        json.dump(levels, outfile)
                    break
                else:
                    print("TIME DIFFERENCE: "+ str(time_difference))
                    print(f'MESSAGE: {msg}')
                    break
@bot.hybrid_command(description='test command')
async def ping(ctx: commands.Context):
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f"Hello {ctx.author}! 💬"))
    await ctx.send('Pong!')


@bot.hybrid_command(description='Steal mee6 levels')
async def steal(ctx: commands.Context):
    stats1 = {}
    for member in ctx.guild.members:
        level = await mee6API.levels.get_user_level(member.id)
        if type(level) != int:
            continue
        stats1[member.id] = [level_barriers[level - 1], level]

    with open("levels1.json", "w") as outfile:
        json.dump(stats1, outfile)

    await ctx.send('data saved to /levels1.json')


@bot.hybrid_command(description='Get invite codes & their uses')
async def stats(ctx: commands.Context):
    embed = discord.Embed(title="Invites", description="Invite codes and their uses!", color=0xff6961)
    for invite in invites[ctx.author.guild.id]:
        if invite.code in invites_youtube:
            embed.add_field(name=f"{invites_youtube[invite.code]}", value=f"{invite.uses}", inline=False)
        else:
            embed.add_field(name=f"{invite.code}", value=f"{invite.uses}", inline=False)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f"Hello {ctx.author}! 💬"))
    await ctx.send(embed=embed)


@bot.hybrid_command(description='Get YouTube invite codes & their uses')
async def yt(ctx: commands.Context):
    embed = discord.Embed(title="YouTube Invites", description="YouTube invite codes and their uses!",
                          color=0xff6961)

    for invite in invites[ctx.author.guild.id]:
        if invite.code in invites_youtube:
            embed.add_field(name=f"{invites_youtube[invite.code]}", value=f"{invite.uses}", inline=False)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f"Hello {ctx.author}! 💬"))
    await ctx.send(embed=embed)


@bot.hybrid_command(description='test embed')
async def test(ctx: commands.Context):
    embed = discord.Embed(title="Welcome to Highpurity's Rose Garden! :rose:",
                          description="• Read our rules at https://discord.com/channels/932430580765839451"
                                      "/932458730509979648 \n • If you need assistance, open a ticket in "
                                      "https://discord.com/channels/932430580765839451/943688886658433104 \n • Check "
                                      "out new YouTube videos in "
                                      "https://discord.com/channels/932430580765839451/932523626807320596",
                          color=0xff6961)
    embed.set_image(
        url="https://66.media.tumblr.com/d3fefcec6a466d1e66bfd4451ddc64c9/tumblr_ozbx86pCdW1w5n1g1o1_500.gif")
    await ctx.send(embed=embed)


@bot.hybrid_command(description="Get Highpurity's YouTube channel's stats", args="kytachipssucks")
async def ytstats(ctx: commands.Context):
    stats = get_channel_stats('UC9308UbLmxNEgOOeKrjrvXw')
    subscribers = stats.get('subscriberCount')
    view_count = stats.get('viewCount')
    video_count = stats.get('videoCount')
    embed = discord.Embed(title="Highpurity's Stats :rose:", color=0xff6961)
    embed.add_field(name='Subscribers', value=subscribers, inline=True)
    embed.add_field(name='Video Count', value=video_count, inline=True)
    embed.add_field(name='View Count', value=view_count, inline=True)
    await ctx.send(embed=embed)


@bot.hybrid_command(description="Get your level!")
async def level(ctx: commands.Context):
    if str(ctx.author.id) not in levels.keys():
        embed = discord.Embed(title=f'ERROR {ctx.author.name}', color=0xff6961)
        embed.add_field(title="ERROR", value="You currently do not have a level!", inline=False)
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(title=f'{ctx.author.name} Level', color=0xff6961)
    embed.add_field(name='Level:', value=levels.get(str(ctx.author.id))[1], inline=True)
    embed.add_field(name='XP:', value=levels.get(str(ctx.author.id))[0], inline=True)
    embed.add_field(name='Next Level:',
                    value="" +
                          str(level_barriers[levels.get(str(ctx.author.id))[0]] - levels.get(str(ctx.author.id))[1])[
                              1] + "XP needed!", inline=True)

    await ctx.send(embed=embed)


bot.run(TOKEN)
