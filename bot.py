import discord
from discord.ext import commands, tasks
from scraper import scrape
from database import get_all, count_houses
from datetime import datetime, timedelta
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL = int(os.getenv("CHANNEL_ID"))

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

def make_progress_bar(done, total, length=10):
    pct = done / total if total else 0
    filled = int(pct * length)
    bar = "█" * filled + "░" * (length - filled)
    return f"{bar} {int(pct*100)}% 😎"

async def scrape_with_progress(ch):
    total_houses = count_houses()  # jeśli cache pusty
    progress_msg = await ch.send(f"⏳ Wczytywanie domków: 0/{total_houses}\n{make_progress_bar(0, total_houses)}")

    def progress_callback(done, total):
        bar = make_progress_bar(done, total)
        # aktualizujemy pasek co 3 sekundy
        bot.loop.create_task(progress_msg.edit(content=f"⏳ Wczytywanie domków: {done}/{total}\n{bar}"))

    await asyncio.to_thread(scrape, progress_callback)
    total_houses = count_houses()
    await progress_msg.edit(content=f"✅ Wczytano {total_houses} domków")
    await check_fast(ch)

async def check_fast(ch):
    for h in get_all():
        dt = parse_date(h[6])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            if h[0] not in alerted_houses:
                alerted_houses.add(h[0])
                await ch.send(
                    f"🔥 **FAST ALERT**\n"
                    f"🏚️ {h[1]} ({h[2]})\n"
                    f"📐 {h[4]} sqm\n"
                    f"👤 {h[5]}\n"
                    f"🕒 {h[6]}\n"
                    f"🗺️ {h[3]}"
                )

@tasks.loop(minutes=15)
async def monitor():
    ch = bot.get_channel(CHANNEL)
    await asyncio.to_thread(scrape)
    await check_fast(ch)

@bot.event
async def on_ready():
    print("Komornik online")
    ch = bot.get_channel(CHANNEL)
    await scrape_with_progress(ch)
    monitor.start()

# Komendy
@bot.command()
async def status(ctx):
    await ctx.send(f"🏠 W cache jest {count_houses()} domków.")

@bot.command()
async def listfast(ctx):
    msg = "🔥 FAST domki ≥13d20h:\n"
    for h in get_all():
        dt = parse_date(h[6])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            msg += f"🏚️ {h[1]} ({h[2]}) | 👤 {h[5]} | 🕒 {h[6]}\n"
    await ctx.send(msg or "Brak FAST domków")

@bot.command()
async def _10(ctx):
    fast_houses = []
    for h in get_all():
        dt = parse_date(h[6])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            fast_houses.append(h)
    fast_houses = sorted(fast_houses, key=lambda x: x[6])[:10]
    msg = "🔥 Top 10 domków do przejęcia:\n"
    for h in fast_houses:
        msg += f"🏚️ {h[1]} ({h[2]}) | 👤 {h[5]} | 🕒 {h[6]}\n"
    await ctx.send(msg or "Brak FAST domków")

bot.run(TOKEN)
