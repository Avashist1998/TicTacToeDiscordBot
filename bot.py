import os
import time
import random
import discord
from itertools import cycle
from dotenv import load_dotenv
from discord.ext import commands , tasks
from tic_tac_toe.TicTacToe import TicTacToe

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents = intents)

GAMES = dict()
GAMES_TIME = dict()

def code_string_maker(string:str):
    return "```" + string + "```"

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    game_cleaner.start()
    for guild in bot.guilds:
        print("{}".format(guild.name))
    print("---------")

@tasks.loop(seconds=100)
async def game_cleaner():
    current_time = time.time()
    game_clean_list = list()
    if len(GAMES_TIME) != 0:
        for name in GAMES_TIME:
            time_diff = current_time - GAMES_TIME[name]
            print(name, time_diff)
            if time_diff > 60:
                game_clean_list.append(name)
        for name in game_clean_list:
            GAMES_TIME.pop(name)
            GAMES.pop(name)

# @bot.event
# async def on_message(message):
#     name = message.author.name
#     content = message.content
#     if message.author != bot.user:
#         print(name)
#         print(content)
#     await bot.process_commands(message)

@bot.command(name='rankUs', help='Ranks all of the member of the chat')
async def rankUs(ctx):
    names = list()
    for user in ctx.guild.members:
        if (user.name != bot.user.name):
            names.append(user.name)
    random.shuffle(names)
    output = ""

    for i, name in enumerate(names):
        output = output + "{}) {}\n".format(i+1,name)
    await ctx.channel.send(output)


async def winner_print(ctx, game):
    await ctx.channel.send(code_string_maker(game.get_board()))
    winner = game.get_winner()
    if (winner == bot.user.name):
        await ctx.channel.send("I have won and you have lost, you fool.\n"\
            "Now leave and take your misrable self away from my gaze")
    elif (winner == ""):
        await ctx.channel.send("You have given me a true challenge. I acknowledge your strength.")
    else:
        await ctx.channel.send("You have tricked me, but whatever the case.\n"\
            "I crown you the winner for all of time.")

@bot.command(name="play")
async def play(ctx, arg1):
    name = ctx.author.name
    content = arg1
    channel = str(ctx.channel)

    if (name != bot.user.name):
        if (channel.name == "Direct Message with {}".format(ctx.author) and name in GAMES):
            if (len(content) == 1 and (int(content) > 0 and int(content) <10)):
                spot = int(content)
                game = GAMES[name]
                status = game.play_turn(spot)
                GAMES_TIME[name] = time.time()
                if (status == -1):
                    await ctx.channel.send("The spot is already taken")
                elif status == 1:
                    await winner_print(ctx, game)
                    GAMES.pop(name)
                    GAMES_TIME.pop(name)
                else:
                    status = bot_play_run(game)
                    GAMES_TIME[name] = time.time()
                    if status == 1:
                        await winner_print(ctx, game)
                        GAMES.pop(name)
                        GAMES_TIME.pop(name)
                    else:
                        await ctx.channel.send(code_string_maker(game.get_board()))
            else:
                await ctx.channel.send("That is not a valid choice. \n"\
                    "The spot must be in between 1 and 9")
        elif (channel.name in GAMES):
            if (len(content) == 1 and (int(content) > 0 and int(content) <10)):
                spot = int(content)
                game = GAMES[channel.name]
                curr_player =  game.player_1 if game.player_1_turn else game.player_2
                if curr_player == ctx.author.name:
                    status = game.play_turn(spot)
                    GAMES_TIME[channel.name] = time.time()
                    if (status == -1):
                        await ctx.channel.send("The spot is already taken")
                    elif status == 1:
                        await ctx.channel.send(code_string_maker(game.get_board()))
                        if (game.winner ==  game.player_1):
                            await ctx.channel.send("Congratuation {}, you have bested {}".format(game.player_1, game.player_2))
                        elif(game.winner == game.player_2):
                            await ctx.channel.send("Congratuation {}, you have bested {}".format(game.player_2, game.player_1))
                        else:
                            await ctx.channel.send("It was had fought battle, but it was a draw. {}, and {} played well".format(game.player_1,game.player_2))
                        GAMES.pop(channel.name)
                        GAMES_TIME.pop(channel.name)
                    elif (status == 1):
                        await ctx.channel.send(code_string_maker(game.get_board()))
                        curr_player =  game.player_1 if game.player_1_turn else game.player_2
                        await ctx.channel.send("It is {} turn".format(curr_player))
                else:
                    await ctx.channel.send("It is not your turn. It is {} turn".format(curr_player))
            else: await ctx.channel.send(code_string_maker(game.get_board()))
        
        else: await ctx.channel.send("There is not game to play 😕")

@bot.command(name="clean-up", pass_context = True)
@commands.has_role('admin')
async def clean_up(ctx, channel_name=None):
    channel = None
    ctx_guild = ctx.guild
    if (channel_name is None):
        channel = ctx.channel
    else:
        for guild_channel in ctx_guild.text_channels:
            if guild_channel.name == channel_name:
                channel = guild_channel
    if channel is None:
        await ctx.channel.send("There is no text channel with that name {}. Please try again".format(channel_name))
    else:
        messages = await channel.history(limit=200).flatten()
        for message in messages:
            if message.author == bot.user:
                await message.delete()
            elif message.content[0] == "$":
                await message.delete()

@bot.command()
async def get_names(ctx):
  names = list()
  for user in ctx.guild.members:
    names.append(user.name)
  await ctx.channel.send('\n'.join(names))

def bot_play_run(game:TicTacToe):
    options = [*range(1,10)]
    random.shuffle(options)
    val = options[8]
    status = game.play_turn(val)
    i = 7
    while(status == -1):
        status = game.play_turn(options[i])
        i = i-1
    return status

def bot_game_maker(names):
    player = names[0]
    bot_player = names[1]
    random.shuffle(names)
    game = TicTacToe(names[0], names[1])
    if (names[0] == bot_player):
        bot_play_run(game)
    GAMES[player] = game
    GAMES_TIME[player] = time.time()

@bot.command(name='playme')
async def playme(ctx):
    challenge = "I am the best tictactoe player in all the servers.\n You fool must pay the price for challenge me"
    member = ctx.author
    player_name = ctx.author.name
    names = [player_name, bot.user.name]
    bot_game_maker(names)
    await member.create_dm()
    await member.send(challenge)
    await member.send("```Type $play spot to pick the spot you want on the board```")
    await member.dm_channel.send(code_string_maker(GAMES[player_name].get_board()))

async def player_game_maker(ctx, names):
    channel_name = names[0]+'_'+names[1]
    await ctx.guild.create_text_channel(channel_name)
    game = TicTacToe(names[0], names[1])
    GAMES[channel_name] = game
    GAMES_TIME[channel_name] = time.time()
    for channel in ctx.guild.channels:
        if channel.name == channel_name: break
    link = await channel.create_invite(max_age = 100, max_uses=2, reason="Invitation for the game held between {}".format(challenge))
    await ctx.channel.send("The game has been create and will be held at channel name {}".format(channel_name))
    await ctx.channel.send(link)
    await ctx.channel.send(code_string_maker(game.get_board()))
    await channel.send("It is {} turn".format(names[0]))

@bot.command(name='challenge')
async def challenge(ctx, arg1):
    userFound = False
    for member in ctx.guild.members:
        # print(member.name)
        if member.name == arg1:
            userFound = True
            if member.status != "online":
                await ctx.channel.send("Player is not available")
            else:
                await player_game_maker(ctx,[ctx.author.name, arg1])
    if not userFound:
        await ctx.channel.send("Player is non-existent")
bot.run(TOKEN)