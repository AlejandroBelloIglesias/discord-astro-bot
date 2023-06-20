import discord
import utils
import keys
from discord.ext.commands import Bot
from typing import Optional


# Send messages
async def sendMessage(message, channel):
    try:
        await channel.send(message)
    except Exception as e:
        print(e)


intents = discord.Intents.default()
intents.message_content = True
bot = Bot("/", intents=intents)


@bot.event
async def on_ready(): #TODO: Esto sirve XD???
    print("Bot is up and ready!")
    try:
        sync = await bot.tree.sync()
        print(f"Synced {len(sync)} commands")
    except:
        print("Error syncing commands.")


@bot.command()
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


@bot.command(name="ping")
async def ping(ctx):
    latency = bot.latency
    await ctx.send(latency)


async def on_success(ctx, result_url, subid):
    user_image = utils.getUserImageFromSubId(subid)
    await ctx.send(f'Image processing SUCCEDED. Result at https://nova.astrometry.net/user_images/{user_image}')
    await ctx.send(result_url)


async def on_failure(ctx, subid):
    user_image = utils.getUserImageFromSubId(subid)
    await ctx.send(f'Image processing FAILED. Result at https://nova.astrometry.net/user_images/{user_image}')
    
async def on_timeout(ctx):
    await ctx.send(f'Image processing is taking too long. Check yourself the result at the previous URL.')


bot.run(keys.DISCORD_TOKEN)
