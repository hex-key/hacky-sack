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
client.remove_command("help")



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

    if not db.search(query.func == "lang"):
        db.insert({"func": "lang", "enabled": ["es"], "es": {"rojo": "red"}, "fr": {"rouge": "red"}})

    global enabled_languages
    enabled_languages = db.search(query.func == "lang")[0]["enabled"]





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
            await message.channel.send("leave me alone. type `$help` for help")

    if message.content.startswith("kys"):
        await message.channel.send("no because it doesn't take being alive to love life")
    
    if message.content.startswith("kms"):
        await message.channel.send("Nooo don't kill yourself your so sexy aha")

    global enabled_languages
    lang_db = db.search(query.func == "lang")[0]
    possible_words = []

    for word in msg.split():
        for lang in enabled_languages:
            lang_dict = lang_db[lang]
            for key in lang_dict.keys():
                if lang_dict[key] == word:
                    possible_words.append((lang, word, key))
    if len(possible_words) > 0:
        trip = random.choice(possible_words)
        await message.channel.send(f"Language check! What is `{trip[1]}` in {trip[0].upper()}? (5s)")
        def check_reply(m):
            return m.author == message.author and m.channel == message.channel
        try:
            m = await client.wait_for("message", timeout=5.0, check=check_reply)
            if m.content.lower() == trip[2]:
                await message.channel.send("You got it! :D")
            else:
                await message.channel.send(f"Not quite! The answer was: `{trip[2]}`")
        except asyncio.TimeoutError:
            await message.channel.send(f"Too slow! The answer was: `{trip[2]}`")
        



    await client.process_commands(message)

#FUN/MISC

#ping msg
@client.command()
async def ping(ctx):
    await ctx.send("pong! latency: " + str(client.latency))

@client.command()
async def flip(ctx):
    sides = ["heads", "tails"]
    flip_result = random.choice(sides)
    await ctx.send(flip_result)

@client.command()
async def tarot(ctx):
    #tarot_list = tarot_db["data"]
    tarot_db = db.get(query.func == "tarot")

    # tarot_list = [ "Fool", "Magician", "High Priestess", "Empress", "Emperor", "Hierophant", "Lovers", "Chariot", "Strength", "Hermit", "Wheel of Fortune", "Justice", "Hanged Man", "Death", "Temperance", "Devil", "Tower", "Star", "Moon", "Sun", "Judgment", "World" ] 
    tarot_list = tarot_db["data"]
    this_card = random.choice(list(tarot_list.keys()))
    await ctx.send(f"Your card is the {this_card} card, which signifies {tarot_list[this_card]}!")

#list of commands
@client.command()
async def help(ctx):
    compliment_jar_commands = "__**COMPLIMENT JAR**__\n`$add_compliment`: adds a compliment to the jar\n`$change_empty_message`: changes the message displayed when jar is empty\n`$compliment_me`: gives you a compliment from the jar\n\n"
    study_commands = "__**STUDYING**__\n`$add_term`: adds term to overall list of terms\n`$all_terms`: sends all terms\n`$import_set`: adds group of terms in their own subgroup\n`$all_sets`: sends list of all sets\n`$quiz_me`: gives you a definition, message back answer to keep going until runs out of terms\n\n"
    fun_commands = "__**FUN COMMANDS**__\n`$flip`: flips a coin\n`$ping`: shows latency"
    await ctx.send(compliment_jar_commands + study_commands + fun_commands)

# COMPLIMENT JAR

#add compliment to "jar"
@client.command()
async def add_compliment(ctx, *, compliment:str):
    c_db = db.get(query.func == "compliments")
    c_list = c_db["data"]

    c_list.append(compliment)

    db.update({"data": c_list}, query.func == "compliments")

    await ctx.send(f"added your compliment to the jar! there are {len(c_list)} compliments in the jar.")

#retrieve compliment from "jar" and remove it
@client.command()
async def compliment_me(ctx):
    c_db = db.get(query.func == "compliments")
    c_list = c_db["data"]
    this_comp = c_db["when_empty"]
    if len(c_list) > 0:
        index = random.randint(0, len(c_list)-1)
        this_comp = c_list[index]
        c_list = c_list[0:index] + c_list[index:]
        db.update({"data": c_list}, query.func == "compliments")
    await ctx.send(this_comp)

#change default empty jar message
@client.command()
async def change_empty_message(ctx, *, message:str):
    db.update({"when_empty" : message}, query.func == "compliments")
    await ctx.send("empty jar message changed :)")



# STUDYING

#add new term to general database
@client.command()
async def add_term(ctx, *, study_term:str):
    term, definition = study_term.split(",", 1)
    c_db = db.get(query.func == "study")
    s_list = c_db["data"]
    s_list[term] = definition
    db.update({"data": s_list}, query.func == "study")
    await ctx.send("added new term: " + study_term)

#return all sets
@client.command()
async def all_sets(ctx):
    s_db = db.get(query.func == "study")
    all_sets_string = "__**SETS**__\n"
    all_sets = [key for key in s_db.keys() if key != "func"]
    for set_name in all_sets:
        all_sets_string += set_name + "\n"
    await ctx.send(all_sets_string)

#return all terms
@client.command()
async def all_terms(ctx, set_name:str="data"):
    s_db = db.get(query.func == "study")
    if set_name in s_db.keys():
        all_terms = s_db[set_name]
        all_terms_string = "__**" + set_name.upper() + "**__\n"
        for key, value in all_terms.items():
            all_terms_string += f"`{key}`: {value}\n"
        await ctx.send(all_terms_string)
    else:
        await ctx.send("Set does not exist.")

# import set like from quizlet or something
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
    except commands.errors.MissingRequiredArgument:
        await ctx.send("Didn't see any text to import! (format: term1,def1;term2,def2; ...)")
    except asyncio.TimeoutError:
        await ctx.send(content="Study set creation timed out.", reference=ctx.message)

#ask questions from the flashcards!
@client.command()
async def quiz_me(ctx, set_name="data"):
    try:
        c_db = db.get(query.func == "study")
        s_list = c_db[set_name]
        print(s_list)
        num = len(s_list)

        correct = 0
        idxs = [i for i in range(num)]
        random.shuffle(idxs)
        for i in idxs:
            q = list(s_list.keys())[i]
            await ctx.send(q)
            def check_reply(m):
                return m.author == ctx.author and m.channel == ctx.channel
            msg = await client.wait_for("message", timeout=30.0, check=check_reply)
            a = msg.content
            if (a == s_list[q]):
                await ctx.send("Your answer was right!")
                correct += 1
            else:
                await ctx.send("You're a bum! The correct answer is " + s_list[q])
        await ctx.send(f"I have nothing left to ask... You got {correct} out of {num}")

    except KeyError:
        await ctx.send("Set does not exist.")
    except asyncio.TimeoutError:
        await ctx.send(content="You died rip", reference=ctx.message)
        


# LANGUAGE IMMERSION

# #return all terms for a language
# @client.command()
# async def all_words(ctx, lang_name):
#     s_db = db.get(query.func == "study")
#     if set_name in s_db.keys():
#         all_terms = s_db[set_name]
#         all_terms_string = "__**" + set_name.upper() + "**__\n"
#         for key, value in all_terms.items():
#             all_terms_string += f"`{key}`: {value}\n"
#         await ctx.send(all_terms_string)
#     else:
#         await ctx.send("Set does not exist.")

# # import set like from quizlet or something
# @client.command()
# async def import_lang(ctx, *, text):
#     try:
#         s_db = db.get(query.func == "study")

#         def check_reply(m):
#             return m.author == ctx.author and m.channel == ctx.channel
#         await ctx.send("Enter a two-character name for this set!")
#         msg = await client.wait_for("message", timeout=60.0, check=check_reply)
#         name = msg.content
#         while db.search(where(name).exists()):
#             await ctx.send("This set already exists, choose a new name or reply `cancel` and use add_term or delete_set.")
#             msg = await client.wait_for("message", timeout=60.0, check=check_reply)
#             name = msg.content
#             if name == "cancel":
#                 await ctx.send("Set creation cancelled.")
#                 return

#         study_set = {}
#         linked_pairs = text.split(";")
#         for linked_pair in linked_pairs:
#             pair = linked_pair.split(",", 1)
#             study_set[pair[0]] = pair[1]
        
#         db.update({name: study_set}, query.func == "study")
#         await ctx.send(f"Language set {name} created!")
#     except commands.errors.MissingRequiredArgument:
#         await ctx.send("Didn't see any text to import! (format: term1,def1;term2,def2; ...)")
#     except asyncio.TimeoutError:
#         await ctx.send(content="Study set creation timed out.", reference=ctx.message)

# #ask questions from the flashcards!
# @client.command()
# async def quiz_me(ctx, set_name="data"):
#     try:
#         c_db = db.get(query.func == "study")
#         s_list = c_db[set_name]
#         print(s_list)
#         num = len(s_list)

#         correct = 0
#         idxs = [i for i in range(num)]
#         random.shuffle(idxs)
#         for i in idxs:
#             q = list(s_list.keys())[i]
#             await ctx.send(q)
#             def check_reply(m):
#                 return m.author == ctx.author and m.channel == ctx.channel
#             msg = await client.wait_for("message", timeout=30.0, check=check_reply)
#             a = msg.content
#             if (a == s_list[q]):
#                 await ctx.send("Your answer was right!")
#                 correct += 1
#             else:
#                 await ctx.send("You're a bum! The correct answer is " + s_list[q])
#         await ctx.send(f"I have nothing left to ask... You got {correct} out of {num}")

#     except KeyError:
#         await ctx.send("Set does not exist.")
#     except asyncio.TimeoutError:
#         await ctx.send(content="You died rip", reference=ctx.message)
        


"""
    RUN
"""
# run the guy
load_dotenv()
client.run(os.getenv('TOKEN'))