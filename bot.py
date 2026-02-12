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

# pomocnicze
def parse_date(s):
    try:
        return datetime.strptime(s, "%d.%m.%Y (%H:%M)")
    except:
        return None

def make_progress_bar(done, total, length=20):
    pct = int(done / total * 100)
    filled = int(length * done / total)
    bar = "█" * filled + "░" * (length - filled)
    return f"{bar} {pct}% 😎"

# progres
async def scrape_with_progress(ch):
    total_houses = count_houses() or 1
    progress_msg = await ch.send(f"⏳ Wczytywanie domków: 0/{total_houses}\n{make_progress_bar(0, total_houses)}")

    progress = {"done": 0}

    def progress_callback(done, total):
        progress["done"] = done

    scrape_task = asyncio.to_thread(scrape, progress_callback)

    while not scrape_task.done():
        done = progress["done"]
        total = count_houses() or 1
        bar = make_progress_bar(done, total)
        await progress_msg.edit(content=f"⏳ Wczytywanie domków: {done}/{total}\n{bar}")
        await asyncio.sleep(3)

    await scrape_task
    total_houses = count_houses()
    bar = make_progress_bar(total_houses, total_houses)
    await progress_msg.edit(content=f"✅ Wczytano {total_houses} domków\n{bar}")
    await check_fast(ch)

# sprawdzanie FAST
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

# monitor co 15 minut
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

# komendy
@bot.command()
async def status(ctx):
    await ctx.send(f"🏠 W cache jest {count_houses()} domków.")

@bot.command()
async def listfast(ctx):
    for h in get_all():
        dt = parse_date(h[6])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            await ctx.send(
                f"🔥 Domek offline ≥13d20h\n"
                f"🏚️ {h[1]} ({h[2]})\n"
                f"📐 {h[4]} sqm\n"
                f"👤 {h[5]}\n"
                f"🕒 {h[6]}\n"
                f"🗺️ {h[3]}"
            )

@bot.command()
async def _10(ctx):
    houses = []
    for h in get_all():
        dt = parse_date(h[6])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            houses.append(h)
    houses = sorted(houses, key=lambda x: parse_date(x[6]))
    for h in houses[:10]:
        await ctx.send(
            f"🔥 Domek offline ≥13d20h\n"
            f"🏚️ {h[1]} ({h[2]})\n"
            f"📐 {h[4]} sqm\n"
            f"👤 {h[5]}\n"
            f"🕒 {h[6]}\n"
            f"🗺️ {h[3]}"
        )

bot.run(TOKEN)
