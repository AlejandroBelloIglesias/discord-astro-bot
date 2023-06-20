import discord
import utils
import keys
from discord.ext.commands import Bot
from typing import Optional


intents = discord.Intents.default()
intents.message_content = True
bot = Bot("/", intents=intents)

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return
    
    if bot.user.mentioned_in(message):
        ctx = await bot.get_context(message)
        attachment: Optional[discord.Attachment] = None
        if len(message.attachments)>0:
            attachment = message.attachments[0]
        await analyze(ctx, attachment)

    await bot.process_commands(message)
        

@bot.command(aliases=["analyse","analize","analise","analysis","process","scan","examine","inspect"])
async def analyze(ctx, attachment: Optional[discord.Attachment]):
    
    # Input error control 
    if attachment is None:
        await ctx.send('You did not upload anything!')
        return
    
    if not utils.isImage(attachment):
        await ctx.send('The attachment is not an image')
        return
    
    # Input OK
    await ctx.send('Processing image ...')

    subid = utils.upload_submission(attachment.url)
    await ctx.send(f'Image processing started at https://nova.astrometry.net/status/{subid}')

    await utils.polling_job(subid=subid,
                            ctx=ctx,
                            success_handler=on_success,
                            failure_handler=on_failure,
                            timeout_handler=on_timeout)


@bot.command()
async def todos(ctx):
    await ctx.send("List of things to be made in the future:\n"+
                   "\t· Make Discord recognize my slash /commands\n"+
                   "\t· Add /help and /command descriptions\n")
    

@bot.command(aliases=["newfeatures","features", "lastfeatures"])
async def patchnotes(ctx):
    await ctx.send("List of last features:\n"+
                   "\t· You can call me with /analise, /analyse, /process, etc. or just @ mention me \n"+
                   "\t· I will @ mention you on result (success, failure or timeout)\n"+
                   "\t· I support multiple requests at the same time (Finally)\n"+
                   "\t· \n")


async def on_success(ctx, result_url, subid):
    user_image = utils.getUserImageFromSubId(subid)
    await ctx.send(f'{ctx.message.author.mention} Image processing SUCCEDED. Result at https://nova.astrometry.net/user_images/{user_image}')
    await ctx.send(result_url)


async def on_failure(ctx, subid):
    user_image = utils.getUserImageFromSubId(subid)
    await ctx.send(f'{ctx.message.author.mention} Image processing FAILED. Result at https://nova.astrometry.net/user_images/{user_image}')
    
async def on_timeout(ctx):
    await ctx.send(f'{ctx.message.author.mention} Image processing is taking too long. Check yourself the result at the previous URL.')


bot.run(keys.DISCORD_TOKEN)
