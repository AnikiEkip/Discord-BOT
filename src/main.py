import asyncio
from collections import defaultdict
import http
import json
import random
from discord.ext import commands
import discord

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True, # Commands aren't case-sensitive
    intents = intents # Set up basic permissions
)

catchphrases = [
    "Banned for having a small dick",
    "Don't want to go with Aniki to the MARDI FOLIES",
    "Laugth when he saw my LoL history",
]

flood_active = False
message_count = defaultdict(int)
time_limit = 5  # Y minutes
message_limit = 5  # X messages

bot.author_id = 309013523147653121  # Change to your discord id

@bot.event
async def on_ready():  # When the bot is ready
    print("I'm in")
    print(bot.user)  # Prints the bot's username and identifier

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "Salut tout le monde":
        await message.channel.send(f"Salut tout seul, {message.author.mention}!")
    await bot.process_commands(message)

@bot.command()
async def pong(ctx):
    await ctx.send('pong')

@bot.command()
async def name(ctx):
    await ctx.send(ctx.author.name)

@bot.command()
async def d6(ctx):
    await ctx.send(random.randint(1, 6))

@bot.command()
async def admin(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Admin")
    if role is None:
        permissions = discord.Permissions(
            manage_channels=True,
            kick_members=True,
            ban_members=True
        )
        await ctx.guild.create_role(name="Admin", permissions=permissions)

    role = discord.utils.get(ctx.guild.roles, name="Admin")
    await member.add_roles(role)

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    if reason is None:
        reason = random.choice(catchphrases)

    await member.ban(reason=reason)
    await ctx.send(f"{member.display_name} has been banned. Reason: {reason}")

@bot.command()
async def flood(ctx):
    global flood_active
    flood_active = not flood_active
    if flood_active:
        await ctx.send("Flood detection activated.")
        bot.loop.create_task(check_flood())
    else:
        await ctx.send("Flood detection deactivated.")

async def check_flood():
    while flood_active:
        for user in message_count.copy():
            message_count[user] -= 1
            if message_count[user] <= 0:
                del message_count[user]
        await asyncio.sleep(60 * time_limit)

@bot.event
async def on_message(message):
    if flood_active:
        author_id = message.author.id
        message_count[author_id] += 1
        if message_count[author_id] > message_limit:
            await message.channel.send(f"⚠️ {message.author.mention}, please refrain from flooding the chat.")
    await bot.process_commands(message)

@bot.command()
async def xkcd(ctx):
    conn = http.client.HTTPSConnection("xkcd.com")
    conn.request("GET", "/info.0.json")
    res = conn.getresponse()
    data = res.read()
    conn.close()

    comic_data = json.loads(data)

    max_image = comic_data['num']

    number = random.randint(1, max_image)
    url = f"{number}/info.0.json"

    conn = http.client.HTTPSConnection("xkcd.com")
    conn.request("GET", url)
    res = conn.getresponse()
    data = res.read()
    conn.close()

    comic_data = json.loads(data)
    comic_url = comic_data['img']

    await ctx.send(f"{comic_url}")

pollMessage = ""

@bot.command()
async def poll(ctx, *, question):
    await ctx.send(f"@here \n👍 or 👎: {question}")
    PollMessage = await ctx.send(f"Poll: {question}")
    await PollMessage.add_reaction('👍')
    await PollMessage.add_reaction('👎')
    

token = ""
bot.run(token)  # Starts the bot