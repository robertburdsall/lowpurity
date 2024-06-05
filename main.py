# bot.py
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

indents = discord.Intents.all()
indents.members = True

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = os.getenv('OWNER_ID')

bot = commands.Bot(command_prefix='/', intents=indents)

invites = {}
invites_youtube = {
    'Yg8rWBzE6E': 'Old',
    'FDaWWTZpWt': 'Old',
    'BNFCsFWkRJ': 'Skoice v3'

}


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
    await bot.tree.sync()


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(932430581374021674)
    await channel.send(f':rose: {member.mention}')
    embed = discord.Embed(title="Welcome to Highpurity's Rose Garden! :rose:", description="• Read our rules at https://discord.com/channels/932430580765839451/932458730509979648 \n • If you need assistance, open a ticket in https://discord.com/channels/932430580765839451/943688886658433104 \n • Check out new YouTube videos in https://discord.com/channels/932430580765839451/932523626807320596", color=0xff6961)
    embed.set_image(url="https://66.media.tumblr.com/d3fefcec6a466d1e66bfd4451ddc64c9/tumblr_ozbx86pCdW1w5n1g1o1_500.gif")
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


@bot.hybrid_command(description='test command')
async def ping(ctx: commands.Context):
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f"Hello {ctx.author}! 💬"))
    await ctx.send('Pong!')


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
    embed = discord.Embed(title="Welcome to Highpurity's Rose Garden! :rose:", description="• Read our rules at https://discord.com/channels/932430580765839451/932458730509979648 \n • If you need assistance, open a ticket in https://discord.com/channels/932430580765839451/943688886658433104 \n • Check out new YouTube videos in https://discord.com/channels/932430580765839451/932523626807320596", color=0xff6961)
    embed.set_image(url="https://66.media.tumblr.com/d3fefcec6a466d1e66bfd4451ddc64c9/tumblr_ozbx86pCdW1w5n1g1o1_500.gif")
    await ctx.send(embed=embed)

bot.run(TOKEN)
