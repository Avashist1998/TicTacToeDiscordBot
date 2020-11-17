import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents = intents)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    for guild in bot.guilds:
        print("{}".format(guild.name))
    print("---------")

@bot.command(name='rankUs', help='Ranks all of the member of the chat')
async def rankUs(ctx):
    names = list()
    ranks = list()

    for user in ctx.guild.members:
        if (user.name != bot.user.name):
            names.append(user.name)
    random.shuffle(names)
    output = ""

    for i, name in enumerate(names):
        output = output + "{}) {}\n".format(i+1,name)
    await ctx.channel.send(output)

@bot.command()
async def get_names(ctx):
  names = list()
  for user in ctx.guild.members:
    names.append(user.name)
    
  await ctx.channel.send('\n'.join(names))

bot.run(TOKEN)