import discord
import utils
import keys
from discord.ext.commands import Bot


# Send messages
async def sendMessage(message, channel):
    try:
        await channel.send(message)
    except Exception as e:
        print(e)


intents = discord.Intents.default()
intents.message_content = True
#client = discord.Client(intents=intents)
bot = Bot("/", intents=intents)


@bot.event
async def on_ready():
    print("Bot is up and ready!")
    try:
        sync = await bot.tree.sync()
        print(f"Synced {len(sync)} commands")
    except:
        print("Error syncing commands.")


"""
@bot.command()
async def analyze(ctx, arg):
  #if len(arg) > 0:
  await ctx.send("Test.")
"""


@bot.command(name="ping")
async def ping(ctx):
    latency = bot.latency
    await ctx.send(latency)


@bot.event
async def on_message(message):
    # Make sure bot doesn't get stuck in an infinite loop
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if message.content == '/analyze' and len(message.attachments) > 0:
        attachment = message.attachments[0]

        if not utils.isImage(attachment):
            await sendMessage('The attachment is not an image', message.channel)
            return

        await sendMessage('Processing image ...', message.channel)
        #try:
        subid = utils.upload_submission(
        attachment.url)  # Await the coroutine object
        await sendMessage(
        f'Image processing started at https://nova.astrometry.net/status/{subid}',
        message.channel)

        await utils.polling_job(subid=subid,
                                channel=message.channel,
                                success_handler=on_success,
                                failure_handler=on_failure)

        #except Exception as e:
        # await sendMessage(
        #  f'Failed to send the image processing petition to the API.\n{e}',
        # message.channel)


async def on_success(channel, result_url, subid):
    user_image = utils.getUserImageFromSubId(subid)
    await sendMessage(
        f'Image processing SUCCEDED. Result at https://nova.astrometry.net/user_images/{user_image}',
        channel)
    await sendMessage(result_url, channel)


async def on_failure(channel, result_url, subid):
    user_image = utils.getUserImageFromSubId(subid)
    await sendMessage(
        f'Image processing FAILED. Result at https://nova.astrometry.net/user_images/{user_image}',
        channel)


bot.run(keys.DISCORD_TOKEN)
