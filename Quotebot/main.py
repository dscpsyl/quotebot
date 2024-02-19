# "brew services start/stop mongodb-community@5.0"
# mongsh command: "mongo"
import json
import logging as log
import sys
from datetime import date
from datetime import datetime
from pathlib import Path

import discord
import pymongo
from discord.ext import commands
from eedit import *

# Loads Settings
with open("settings.json", "r") as settingsFile:
    settings: dict = json.load(settingsFile)

# Logging
log.basicConfig(level=log.INFO)

# Format the logs
logFormat = log.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s::%(funcName)s - %(message)s"
)
rootLogger = log.getLogger()

# Handle the logs into a file
logFile = f"logs/quotebot-{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}.log"
Path(logFile).touch(exist_ok=True)
fileLogger = log.FileHandler(logFile)
fileLogger.setFormatter(logFormat)
rootLogger.addHandler(fileLogger)

# Handle the logs into the console
consoleLogger = log.StreamHandler(sys.stdout)
consoleLogger.setFormatter(logFormat)
rootLogger.addHandler(consoleLogger)

# Set the premissions for the bot
intents: discord.Intents = discord.Intents.default()
intents.message_content = True

# Loads Bot
bot = commands.Bot(
    command_prefix=settings["prefix"], intents=intents, help_command=None
)

# Loads db
myclient: pymongo.MongoClient = pymongo.MongoClient(settings["mongoClientID"])
mydb = myclient[settings["databaseName"]]
mycol = mydb[settings["collectionName"]]

# Set the quote number to the last quote number in the database
no: int = 1
for doc in mycol.find({}, {"_id": 1}).sort("_id", -1).limit(1):
    no: int = doc["_id"] + 1


@bot.event
async def on_ready():
    global no
    log.info(
        f'{bot.user} is connected and has the db of: {str(str(mydb).split(" ")[-1:])[2:-3]} with collection: {str(str(mycol).split(" ")[-1:])[2:-3]}'
    )
    log.info(f"Initalized quote number: {no}")


@bot.event
async def on_message(message: discord.Message):

    # Check for command prefixes and process commands
    prefix = settings["prefix"]
    if message.content.startswith(prefix):
        await bot.process_commands(message)
        return

    global no  # global quote number

    # Check of the message is in the channel we are looking for
    channelWatch = settings["ChannelID"]
    if str(message.channel.id) != channelWatch:
        return

    # Check if the message is from the bot
    if message.author == bot.user:
        return

    # Check to see if there is one mention of an author
    authorList: list = message.mentions
    if len(authorList) > 1 or len(authorList) == 0:
        await message.delete()
        await message.channel.send(
            f"Error: Please only specify one author for this quote at this time we found {len(authorList)}: {[user.name for user in authorList]} in quote: {message.content}.",
            delete_after=60,
        )
        log.warning(
            f"{message.author} tried to add a quote with {len(authorList)} authors: {[user.name for user in authorList]} and content: {message.content}"
        )
        return
    quoteAuthor: discord.Member = authorList[0]
    quoteSender: discord.User | discord.Member = message.author

    # Get a mentionable string for the author
    authorMentionString: str = quoteAuthor.mention

    # Get the content of the message and make sure the citation is at the end of the message
    quoteContent: str | list = message.content
    quoteContent = quoteContent.split(" ")
    quote: str = " ".join(quoteContent[:-1])
    if quoteContent[-1] != authorMentionString:
        await message.delete()
        await message.channel.send(
            f"Error: Please make sure to mention the author at the end of the quote For example: {quote} @citation.",
            delete_after=60,
        )
        log.warning(
            f"{message.author} tried to add a quote without mentioning the author at the end of the quote: {quote}"
        )
        return

    # Get's current year for citationå
    today: date = date.today()
    time: datetime | str = datetime.now()
    time = time.strftime("%H:%M:%S")
    year: int = today.year

    # Sanitize the quote to prevent * from messing up the formatting
    sanitizedQuote = quote.replace("*", "\\*")

    # Sends formatted message & cleans up
    fullQuote = (
        str(no) + ": "
        '***"'
        + sanitizedQuote
        + '"'
        + ".*** `(`"
        + authorMentionString
        + "`, "
        + str(year)
        + ")`"
    )
    quote_message = await message.channel.send(fullQuote)
    jumpURL: str = quote_message.jump_url
    await message.delete()
    # Invisible character for double spacing
    await message.channel.send("\u3164")

    # Write to Database
    mycol.insert_one(
        {
            "_id": no,
            "quote": quote,
            "author": str(quoteAuthor),
            "sender": str(quoteSender),
            "time": str(time),
            "day": str(today),
            "url": str(jumpURL),
        }
    )

    # print to console
    log.info(
        f'Added quote no: {no} to database: "{quote}", {quoteAuthor.name} from {quoteSender.name}. `{str(jumpURL)}`'
    )

    no += 1


# ? Args0 will be option of edit | args1 will be quote to edit
@bot.command(name="e", help="Edits previous quotes in database")
async def edit(ctx, *args):
    if len(args) == 0:
        await ctx.message.delete()
        await ctx.send(
            "Error: No arguments supplied. The current available options are: |author|, |quote|.",
            delete_after=5,
        )
        return

    if args[0] == "author":
        await authorEdit(ctx, mycol, *args)
        log.info(f"Author edit: {args[1]}")
    elif args[0] == "quote":
        await quoteEdit(ctx, mycol, *args)
        log.info(f"Quote edit: {args[1]}")
    else:
        await ctx.message.delete()
        await ctx.send(
            "Error: That is not a current valid editing opiton", delete_after=5
        )


@bot.command(name="p", help="Set the prefix of quote")
async def prefixSetting(ctx, *args):
    if len(args) == 0:
        await ctx.message.delete()
        await ctx.send("Error: No arguments supplied.")
        return
    elif len(args) != 1:
        await ctx.message.delete()
        await ctx.send("Error: Please input only one prefix")
        return

    if args[0] == "":
        await ctx.message.delete()
        await ctx.send("Error: Please input a valid prefix")
        return

    # Keep the quote channel clean
    if str(ctx.message.channel.id) == settings["ChannelID"]:
        await ctx.message.delete()

    bot.command_prefix = args[0]
    await ctx.send(f"Updated prefix to {args[0]}!", delete_after=60)
    log.info(f"Updated prefix to {args[0]}!")

    with open("settings.json", "r+") as settingsFile:
        settingsData = json.load(settingsFile)
        settingsData["prefix"] = str(args[0])
        settingsFile.seek(0)
        json.dump(settingsData, settingsFile, indent=4)
        settingsFile.truncate()


@bot.command(name="c", help="Change the channel that the quotebot listens in")
async def channelChange(ctx, *args):
    if len(args) != 1:
        await ctx.message.delete()
        await ctx.send(
            "Error: please tag only one channel that will be the quote channel."
        )

    if args[0][0] != ctx.message.channel.mention[0]:
        await ctx.message.delete()
        await ctx.send("Error: Please tag the channel with the # symbol.")
        return

    # Get the channel ID from the arg
    newChannelID = str(args[0][2:-1])
    settings["ChannelID"] = newChannelID

    with open("settings.json", "w") as settingsFile:
        settingsFile.seek(0)
        json.dump(settings, settingsFile, indent=4)
        settingsFile.truncate()

    # Keep the quote channel clean
    if str(ctx.message.channel.id) == newChannelID:
        await ctx.message.delete()

    await ctx.send(f"Updated the listening channel to {args[0]}!", delete_after=60)
    log.info(f"Updated the listening channel to {args[0]}!")


bot.run(settings["BotToken"])
