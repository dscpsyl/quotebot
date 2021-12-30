async def authorEdit(ctx,mycol,*args):
    if len(args) != 3:
            await ctx.message.delete()
            await ctx.send("Error: The arguments are incorrect. The format is: \"e author [Quote Index No.] [New Author]", delete_after=5)
            return
        
    #Gets new Author Information
    newAuthorID = ctx.message.content[ctx.message.content.find('<'):ctx.message.content.find('>')+1]
    newAuthor = ctx.message.mentions[0]
        
    #Updates Database
    result = mycol.update_one({"_id":int(args[1])},{"$set":{"author":str(newAuthor)}})
    if result.acknowledged:
        await ctx.send(f"Updated the quthor of quote {str(args[1])} to {str(newAuthor)}", delete_after=5)
    else:
        await ctx.send("Error: Failed to update quote.")
        
    #Update Visible Book
        
        
        
    for entry in mycol.find({"_id":int(args[1])}):
        print(entry['author'])
          
          
                  
    await ctx.message.delete()