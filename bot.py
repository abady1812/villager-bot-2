import discord
from discord.ext import commands
import os
import asyncio
import traceback

TOKEN = os.getenv("DISCORD_TOKEN")
CATEGORY_ID = int(os.getenv("CATEGORY_ID", 0))

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ Error in {event}: {args} {kwargs}")

@bot.event
async def on_command_error(ctx, error):
    print(f"Command error: {error}")
    traceback.print_exc()

@bot.event
async def on_guild_channel_create(channel):
    if channel.category_id != CATEGORY_ID:
        return

    await asyncio.sleep(3)

    target_user = None
    found_embed_text = False

    async for message in channel.history(limit=10):
        if message.mentions and len(message.mentions) > 0:
            target_user = message.mentions[0]

        if message.embeds:
            for embed in message.embeds:
                embed_content = ""
                if embed.title:
                    embed_content += embed.title + " "
                if embed.description:
                    embed_content += embed.description + " "
                if embed.fields:
                    for field in embed.fields:
                        embed_content += field.name + " " + field.value + " "

                if "Send your statics here" in embed_content:
                    found_embed_text = True

    if found_embed_text and target_user:
        await channel.send(f"{target_user.mention}\nابعت الإحصائيات بالشكل ده")
        await channel.send("https://i.postimg.cc/WzRJ0m4V/image-1.png")
        print("✅ Bot responded to ticket!")
    else:
        print(f"❌ Bot didn't respond - Embed: {found_embed_text}, User: {target_user}")

bot.run(TOKEN)
