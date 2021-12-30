#fetches data for the old message to be edited 
def orgMsgFind(mycol,idxNo):
    for entry in mycol.find({"_id":int(idxNo)}):
        return entry['url'].split('/')[-1]

async def updateDatabase(ctx,mycol,field,data,*args):
    result = mycol.update_one({"_id":int(args[1])},{"$set":{field:str(data)}})
    if result.acknowledged:
        await ctx.send(f"Updated the {field} of quote {str(args[1])} to {str(data)}", delete_after=5)
    else:
        await ctx.send("Error: Failed to update quote.")    


#Finds previous quote by index no. 
#gets revelant jumurl from database
#gets what to edit from arguments 
#edits the content on both the database and the discord text channel 


async def authorEdit(ctx,mycol,*args):
    if len(args) != 3:
            await ctx.message.delete()
            await ctx.send("Error: The arguments are incorrect. The format is: \"e author [Quote Index No.] [New Author Tag]", delete_after=5)
            return
        
    #Gets new Author Information
    newAuthorID = ctx.message.content[ctx.message.content.find('<'):ctx.message.content.find('>')+1]
    newAuthor = ctx.message.mentions[0]
        
    updateDatabase(ctx, mycol,"author",newAuthor,*args)

    #Update Visible Book 
    quoteID = orgMsgFind(mycol,args[1])
    orgMsg = await ctx.channel.fetch_message(quoteID) 
    oldAuthorID = orgMsg.content[orgMsg.content.find('<'):orgMsg.content.find('>')+1]
    newMsg = str(orgMsg.content).replace(oldAuthorID,newAuthorID)
    await orgMsg.edit(content=newMsg)
               
    await ctx.message.delete()
    
async def quoteEdit(ctx,mycol,*args):
    if len(args) != 3:
            await ctx.message.delete()
            await ctx.send("Error: The arguments are incorrect. The format is: \"e author [Quote Index No.] \"[New Quote]\"", delete_after=5)
            return    
    
    newQuote = str(args[2])
    
    updateDatabase(ctx,mycol,"quote",newQuote,*args)
    
    
    
    
    
    await ctx.message.delete()

