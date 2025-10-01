import os
import asyncio
import traceback
import discord
from discord.ext import commands
from aiohttp import web

# ---------- إعداد المتغيّرات ----------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CATEGORY_ID = int(os.getenv("CATEGORY_ID", 0))
PORT = int(os.getenv("PORT", 8000))  # Render يعطي PORT تلقائياً

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- سيرفر ويب خفيف علشان Render يبقي الخدمة صحية ----------
async def handle_root(request):
    return web.Response(text="Villager Bot is running ✅")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Web server started on port {PORT}")

# ---------- أحداث البوت ----------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    # نبدأ سيرفر الويب كـ task في نفس الحلقة
    bot.loop.create_task(start_web_server())

@bot.event
async def on_command_error(ctx, error):
    print("Command error:", error)
    traceback.print_exc()

@bot.event
async def on_guild_channel_create(channel):
    try:
        print("Channel created:", channel.name, "id:", channel.id, "category_id:", channel.category_id)
        if channel.category_id != CATEGORY_ID:
            print("Not target category.")
            return

        await asyncio.sleep(2)

        target_user = None
        found_embed_text = False

        async for message in channel.history(limit=20):
            if message.mentions:
                target_user = message.mentions[0]
            if message.embeds:
                for embed in message.embeds:
                    embed_content = ""
                    if embed.title: embed_content += embed.title + " "
                    if embed.description: embed_content += embed.description + " "
                    if embed.fields:
                        for field in embed.fields:
                            embed_content += f"{field.name} {field.value} "
                    # لو نص الـ embed عندك عربي/انجليزي غيّره هنا
                    if "Send your statics here" in embed_content:
                        found_embed_text = True

        if found_embed_text and target_user:
            await channel.send(f"{target_user.mention}\nابعت الإحصائيات بالشكل ده")
            await channel.send("https://i.postimg.cc/WzRJ0m4V/image-1.png")
            print("✅ Responded to ticket")
        else:
            print("Not responding: found_embed_text:", found_embed_text, "target_user:", target_user)

    except Exception as e:
        print("Error in on_guild_channel_create:", e)
        traceback.print_exc()

# ---------- شغّل البوت ----------
if not DISCORD_TOKEN:
    print("Missing DISCORD_TOKEN env variable. Exiting.")
else:
    bot.run(DISCORD_TOKEN)
