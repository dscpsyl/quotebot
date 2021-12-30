# "brew services start/stop mongodb-community@5.0"
# mongsh command: "mongo"
import discord
import json
import pymongo
import os
from discord.ext import commands
from datetime import date, datetime
from eedit import *

from pymongo.message import delete

#Loads Settings
with open("settings.json", "r") as settingsFile:
    settings = json.load(settingsFile)

#Loads Bot
bot = commands.Bot(command_prefix=settings["prefix"])

#Loads db
myclient = pymongo.MongoClient(settings["mongoClientID"])
mydb = myclient[settings["databaseName"]]
mycol = mydb[settings["collectionName"]]

for doc in mycol.find({}, {"_id":1}).sort("_id", -1).limit(1):
    no = doc["_id"] + 1

@bot.event
async def on_ready():
    print(f'{bot.user} is connected and has the db of: {str(str(mydb).split(" ")[-1:])[2:-3]} with collection: {str(str(mycol).split(" ")[-1:])[2:-3]}')
    print(f"Initalized no: {no}")

@bot.command(name="q", help="Quote's the message you sent")
async def quote(ctx):
    global no
    #Checks to find quote
    quote = ctx.message.content[3:]
    quotePOS = [pos for pos, char in enumerate(quote) if char == '"']
    if len(quotePOS) != 2:
        await ctx.message.delete()
        await ctx.send("Error: Can't Find Quote. Please surround your quote with quotation marks.", delete_after=5)
        return

    quoteReturn = quote[quotePOS[0]+1:quotePOS[1]]

    #Checks to find a single author and their username
    authorList = ctx.message.mentions
    if len(authorList) > 1 or len(authorList) ==0:
        await ctx.message.delete()
        await ctx.send("Error: Please only specify one author at this time.", delete_after=5)
        return
    author = authorList[0]
    sender = ctx.message.author

    #Finds author userid so it can be mentioned
    authorID = quote[quote.find("<"):quote.find(">")+1]

    #Get's current year for citationå
    today = date.today()
    time = datetime.now()
    time = time.strftime("%H:%M:%S")
    year = today.year

    #Sends formated message & cleans up
    await ctx.send(str(no) + ": "'***"'+str(quoteReturn)+'"'+".*** `(`"+str(authorID)+"`, "+str(year)+")`")
    jumpURL = ctx.channel.last_message.jump_url
    await ctx.message.delete()
    #Invisible character for double spacing
    await ctx.send("\u3164")

    #Write to Database
    mycol.insert_one({"_id" : no, "quote" : quoteReturn, "author" : str(author), "sender" : str(sender), "time" : str(time), "day" : str(today), "url" : str(jumpURL)})
    no += 1
    

#? Args0 will be option of edit | args1 will be quote to edit
@bot.command(name="e", help="Edits previous quotes in database")
async def edit(ctx, *args):
    if len(args) == 0:
        await ctx.message.delete()
        await ctx.send("Error: No arguments supplied. The current available options are: |author|, |quote|.", delete_after=5)
        return

    if args[0] == "author":
        await authorEdit(ctx,mycol,*args)
    elif args[0] == "quote":
        await quoteEdit(ctx,mycol,*args)
    else:
        await ctx.message.delete()
        await ctx.send("Error: That is not a current valid editing opiton", delete_after=5)

#!Not Functional
@bot.command(name="p", help="Set the prefix of quote")
async def prefixSetting(ctx, *args):
    pass

#!Not Functional
@bot.command(name="c", help="Set's the channel ID of where the quotes are")
async def channelSetting(ctx):
    pass
    #Channel ID

#!Not Functional
@bot.command(name="o", help="Initial Setup when the bot joins")
async def setUp(ctx):
    pass
    #create quotebook channel if it doens't exist and rememebr channel id in settings

#!Not Functional
@bot.command(name="s", help="Searches through database for old quotes")
async def formatSetting(ctx):
    pass
    #search database

bot.run(settings["BotToken"])