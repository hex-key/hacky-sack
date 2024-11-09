"""
    SETUP
"""

# imports
import discord
import os
from tinydb import TinyDB, Query
from discord.ext import commands
from dotenv import load_dotenv

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


# process every new message
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

# COMMANDS

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("kys"):
        await message.channel.send("no because it doesn't take being alive to love life")

# run the guy
load_dotenv()

client.run(os.getenv('TOKEN'))