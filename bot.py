import discord
from discord.ext import commands, tasks
from scraper import scrape
from database import get_all, count_houses
from datetime import datetime, timedelta
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL = int(os.getenv("CHANNEL_ID"))

# Discord intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FAST_THRESHOLD = timedelta(days=13, hours=20)
alerted_houses = set()

def parse_date(s):
    try:
        return datetime.strptime(s, "%d.%m.%Y (%H:%M)")
    except:
        return None

# 🔹 Wczytywanie domków z paskiem postępu
async def scrape_with_progress(ch):
    progress_msg = await ch.send("⏳ Wczytywanie domków: 0/…")

    def progress_callback(done, total):
        # Szacowany % i wizualny pasek
        percent = int(done / total * 100)
        bar_len = 10
        filled = int(bar_len * percent / 100)
        bar = "█"*filled + "░"*(bar_len - filled)
        # Szacowany czas końca
        est_time = (total - done) * 1  # sekundy na domek, przybliżone
        est_str = str(timedelta(seconds=int(est_time)))
        content = f"⏳ Wczytywanie domków: {done}/{total} ({percent}%) {bar} ⏱️ ETA {est_str}"
        bot.loop.create_task(progress_msg.edit(content=content))

    await asyncio.to_thread(scrape, progress_callback)
    await progress_msg.edit(content=f"✅ Wczytano {count_houses()} domków")
    await check_fast(ch)

# 🔹 Sprawdzenie FAST i alert
async def check_fast(ch):
    for h in get_all():
        dt = parse_date(h[5])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            if h[0] not in alerted_houses:
                alerted_houses.add(h[0])
                await ch.send(
                    f"🔥 **FAST ALERT**\n"
                    f"🏚️ {h[0]} ({h[1]})\n"
                    f"📐 {h[3]} sqm\n"
                    f"👤 {h[4]}\n"
                    f"🕒 {h[5]}\n"
                    f"🗺️ {h[2]}"
                )

# 🔹 Monitor co 15 minut
@tasks.loop(minutes=15)
async def monitor():
    ch = bot.get_channel(CHANNEL)
    await asyncio.to_thread(scrape)
    await check_fast(ch)

# 🔹 Bot gotowy
@bot.event
async def on_ready():
    print("Komornik online")
    ch = bot.get_channel(CHANNEL)
    await scrape_with_progress(ch)
    monitor.start()

# 🔹 Komendy
@bot.command()
async def status(ctx):
    await ctx.send(f"🏠 W cache jest {count_houses()} domków.")

@bot.command()
async def listfast(ctx):
    for h in get_all():
        dt = parse_date(h[5])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            await ctx.send(
                f"🔥 Domek offline ≥13d20h\n"
                f"🏚️ {h[0]} ({h[1]})\n"
                f"📐 {h[3]} sqm\n"
                f"👤 {h[4]}\n"
                f"🕒 {h[5]}\n"
                f"🗺️ {h[2]}"
            )

# 🔹 NOWA KOMENDA !10
@bot.command()
async def domki10(ctx):
    """Pokaż 10 domków do przejęcia (≥13d20h offline)"""
    selected = []
    for h in get_all():
        dt = parse_date(h[5])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            selected.append(h)
        if len(selected) >= 10:
            break

    if not selected:
        await ctx.send("Nie znaleziono domków do przejęcia 😎")
        return

    for h in selected:
        await ctx.send(
            f"🔥 Domek offline ≥13d20h\n"
            f"🏚️ {h[0]} ({h[1]})\n"
            f"📐 {h[3]} sqm\n"
            f"👤 {h[4]}\n"
            f"🕒 {h[5]}\n"
            f"🗺️ {h[2]}"
        )

bot.run(TOKEN)
