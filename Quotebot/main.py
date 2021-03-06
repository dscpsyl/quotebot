#TODO: be able to save images as well, send quote to a single channel only

import discord 
import json
import pymongo
from discord.ext import commands
from datetime import date, datetime 

#Loads Settings
with open("settings.json", "r") as settingsFile:
    settings = json.load(settingsFile)

#Loads Bot 
botPrefix = settings["prefix"]
bot = commands.Bot(command_prefix=botPrefix)
TOKEN = settings["BotToken"]

#Loads db
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["QuoteBot"]
mycol = mydb["quotesArchive"] 

for doc in mycol.find({}, {"_id":1}).sort("_id", -1).limit(1):
    no = doc["_id"] + 1

@bot.event
async def on_ready():
    print(f'{bot.user} is connected and has the db of: {str(str(mydb).split(" ")[-1:])[2:-3]} with collection: {str(str(mycol).split(" ")[-1:])[2:-3]}')

@bot.command(name="q", help="Quote's the message you sent")
async def quote(ctx):
    global no
    #Checks to find quote
    quote = ctx.message.content[3:]
    quotePOS = [pos for pos, char in enumerate(quote) if char == '"']
    if len(quotePOS) != 2:
        await ctx.send("Error: Can't Find Quote. Please surround your quote with quotation marks.")
        await ctx.message.delete()
        return
    
    quoteReturn = quote[quotePOS[0]+1:quotePOS[1]]
    
    #Checks to find a single author and their username
    authorList = ctx.message.mentions
    if len(authorList) > 1:
        await ctx.send("Error: Please only specify one author at this time.")
        await ctx.message.delete()
        return
    elif len(authorList) == 0:
        await ctx.send("Error: Please only specify an author.")
        await ctx.message.delete()
        return
    author = authorList[0]
    sender = ctx.message.author
    jumpURL = ctx.message.jump_url
    
    #Finds author userid so it can be mentioned
    authorID = quote[quote.find("<"):quote.find(">")+1]
    
    #Get's current year for citation 
    today = date.today() 
    time = datetime.now()
    time = time.strftime("%H:%M:%S")
    year = today.year

    #Sends formated message & cleans up 
    await ctx.send(str(no) + ": "'***"'+str(quoteReturn)+'"'+".*** `(`"+str(authorID)+"`, "+str(year)+")`")
    await ctx.message.delete()
    #Invisible character for double spacing
    await ctx.send("\u3164")
    
    #Write new Entry
    mycol.insert_one({"_id" : no, "quote" : quoteReturn, "author" : str(author), "sender" : str(sender), "time" : str(time), "day" : str(today), "url" : str(jumpURL)})
    no += 1

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
@bot.command(name="f", help="How to format the quote (APA, MAL, Chicago, etc.)")
async def formatSetting(ctx):
    pass
    #define different quoting styles

#!Not Functional 
@bot.command(name="s", help="Searches through database for old quotes")
async def formatSetting(ctx):
    pass
    #search database

bot.run(TOKEN)    
