"""
    SETUP
"""

# imports

import os
from dotenv import load_dotenv
import asyncio
import random

import discord
from discord.ext import commands

from tinydb import TinyDB, Query, where

from utils import *
from utils_lang import *

# set up json database
db = TinyDB("db.json")
query = Query()


# set up discord app intents and shit
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(intents=intents, command_prefix='$', case_insensitive=True)




# EVENT LISTENERS

# print to terminal when logged in
@client.event
async def on_ready():
    # confirm signs of life
    print(f'Logged in as {client.user}')
    await client.change_presence(status=discord.Status.dnd, activity=discord.CustomActivity(name="suffering"))

    # fix db stuff
    if not db.search(query.func == "compliments"):
        db.insert({"func": "compliments", "when_empty": "your jar is empty...but it's ok, i love you! <3", "data": []})
    
    if not db.search(query.func == "study"):
        db.insert({"func": "study", "data": {}})




"""
    HELPER FUNCTIONS
"""

"""
    FUNCTIONALITY
"""

# EVENT LISTENERS


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
    
    if message.content.startswith("kms"):
        await message.channel.send("Nooo don't kill yourself your so sexy aha")

    if "something" in message.content:
        pass

    await client.process_commands(message)



# COMMANDS

@client.command()
async def ping(ctx):
    await ctx.send("pong! latency: " + str(client.latency))

@client.command()
async def add_compliment(ctx, *, compliment:str):
    c_db = db.get(query.func == "compliments")
    c_list = c_db["data"]

    c_list.append(compliment)

    db.update({"data": c_list}, query.func == "compliments")

    await ctx.send(f"added your compliment to the jar! there are {len(c_list)} compliments in the jar.")

@client.command()
async def compliment_me(ctx):
    c_db = db.get(query.func == "compliments")
    c_list = c_db["data"]
    this_comp = c_db["when_empty"]
    if len(c_list) > 0:
        this_comp = c_list.pop(random.randint(0, len(c_list) - 1))
        db.update({"data": c_list}, query.func == "compliments")
    await ctx.send(this_comp)

@client.command()
async def change_empty_message(ctx, *, message:str):
    db.update({"when_empty" : message}, query.func == "compliments")
    await ctx.send("empty jar message changed :)")

@client.command()
async def add_term(ctx, *, study_term:str):
    division_index = study_term.index(",")
    term = study_term[0, division_index]
    definition = study_term[division_index + 1, len(study_term)]
    c_db = db.get(query.func == "study")
    s_list = c_db["data"]
    newTerm = {term, definition}
    s_list.append(newTerm)
    db.update({"data": s_list}, query.func == "study")
    await ctx.send("added new term: " + study_term)


@client.command()
async def import_set(ctx, *, text):
    
    try:
        s_db = db.get(query.func == "study")

        def check_reply(m):
            return m.author == ctx.author and m.channel == ctx.channel
        await ctx.send("Enter a name for this set!")
        msg = await client.wait_for("message", timeout=60.0, check=check_reply)
        name = msg.content
        while db.search(where(name).exists()):
            await ctx.send("This set already exists, choose a new name or reply `cancel` and use add_term or delete_set.")
            msg = await client.wait_for("message", timeout=60.0, check=check_reply)
            name = msg.content
            if name == "cancel":
                await ctx.send("Set creation cancelled.")
                return

        study_set = {}
        linked_pairs = text.split(";")
        for linked_pair in linked_pairs:
            pair = linked_pair.split(",", 1)
            study_set[pair[0]] = pair[1]
        
        db.update({name: study_set}, query.func == "study")
        await ctx.send(f"Study set {name} created!")

    except asyncio.TimeoutError:
        await ctx.send(content="Study set creation timed out.", reference=ctx.message)




@client.command()
async def flip(ctx):
    sides = ["heads", "tails"]
    flip_result = random.choice(sides)
    await ctx.send(flip_result)

# run the guy
load_dotenv()

client.run(os.getenv('TOKEN'))