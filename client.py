# bot.py
import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    print("{} is connected to the following guild:\n{}(id: {})".format(
        client.user, guild.name, guild.id))
    members = '\n - '.join([member.name for member in guild.members])
    print('Guild Members:\n - {}'.format(members))

@client.event
async def on_member_join(member):
    WelcomeString = "The goal for the server is to create a space for testing my bot."
    await member.create_dm()
    await member.dm_channel.send("Hi {}, wewlcome to my Discord server!".format(
        member.name))
    await member.dm_channel.send(WelcomeString)

@client.event
async def on_message(message):
    happy_birthday = 'Happy Birthday! 🎈🎉'
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]
    if message.author != client.user:
        if 'happy birthday' in message.content.lower():
                await message.channel.send(happy_birthday)

        if message.content == '99!':
            response = random.choice(brooklyn_99_quotes)
            await message.channel.send(response)
        elif message.content == 'raise-exception':
            raise discord.DiscordException


@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

@bot.event
async def on_read():
    print("{} has connect to the Discord!".format(bot.user.name))

client.run(TOKEN)