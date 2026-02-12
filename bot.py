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

def progress_bar(done, total, length=10):
    perc = done / total if total else 0
    filled = int(length * perc)
    bar = "█" * filled + "░" * (length - filled)
    return f"{bar} {int(perc*100)}% 😎"

async def scrape_with_progress(ch):
    progress_msg = await ch.send("⏳ Wczytywanie domków: 0/…")
    start_time = datetime.utcnow()
    progress_data = {"done": 0, "total": 0, "finished": False}

    # Callback wywoływany w scraperze przy każdym domu/stronie
    def progress_callback(done, total):
        progress_data["done"] = done
        progress_data["total"] = total

    async def update_progress():
        while not progress_data["finished"]:
            done = progress_data["done"]
            total = progress_data["total"]
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            rate = done / elapsed if elapsed > 0 else 0
            remaining = int((total - done) / rate) if rate > 0 else 0
            eta = str(timedelta(seconds=remaining)).split(".")[0]
            bar = progress_bar(done, total)
            await progress_msg.edit(content=f"⏳ Wczytywanie domków: {done}/{total} | ETA: {eta}\n{bar}")
            await asyncio.sleep(3)

    updater_task = asyncio.create_task(update_progress())
    await asyncio.to_thread(scrape, progress_callback)
    progress_data["finished"] = True
    await updater_task
    await progress_msg.edit(content=f"✅ Wczytano {count_houses()} domków")
    await check_fast(ch)

async def check_fast(ch):
    for h in get_all():
        dt = parse_date(h[5])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            if h[0] not in alerted_houses:
                alerted_houses.add(h[0])
                await ch.send(
                    f"🔥 **FAST ALERT**\n"
                    f"🏚️ {h[1]} ({h[2]})\n"
                    f"📐 {h[4]} sqm\n"
                    f"👤 {h[3]}\n"
                    f"🕒 {h[5]}\n"
                    f"🗺️ {h[2]}"
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
                f"🏚️ {h[1]} ({h[2]})\n"
                f"📐 {h[4]} sqm\n"
                f"👤 {h[3]}\n"
                f"🕒 {h[5]}\n"
                f"🗺️ {h[2]}"
            )

@bot.command()
async def _10(ctx):
    candidates = []
    for h in get_all():
        dt = parse_date(h[5])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            candidates.append(h)
    for h in candidates[:10]:
        await ctx.send(
            f"🔥 Domek offline ≥13d20h\n"
            f"🏚️ {h[1]} ({h[2]})\n"
            f"📐 {h[4]} sqm\n"
            f"👤 {h[3]}\n"
            f"🕒 {h[5]}\n"
            f"🗺️ {h[2]}"
        )

bot.run(TOKEN)
