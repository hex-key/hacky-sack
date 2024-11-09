"""
    SETUP
"""

# imports
import discord
import os
from tinydb import TinyDB, Query
from discord.ext import commands
from dotenv import load_dotenv

from utils_lang import *

# set up json database
db = TinyDB('db.json')


# set up discord app intents and shit
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


"""
    FUNCTIONALITY
"""

# EVENT LISTENERS

# print to terminal when logged in
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(status=discord.Status.dnd, activity=discord.CustomActivity(name="suffering"))



# process every new message
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower()

    for i in message.mentions:
        if i.id == client.user.id:
            await message.channel.send("leave me alone")

    if message.content.startswith("kys"):
        await message.channel.send("no because it doesn't take being alive to love life")

# COMMANDS


# run the guy
load_dotenv()

client.run(os.getenv('TOKEN'))